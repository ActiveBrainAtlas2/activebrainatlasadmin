"""This module is responsible for the saving and restoring of the three different annotations.

A. Saving annotations - when the user clicks 'Save annotations' in Neuroglancer:


1. All data from the active layer gets sent to one of the three tables:
   
   * Marked cells
   * Polygon sequences
   * Structure COM

2. Data also gets sent to the annotations_point_archive table. This table has a unique
constraint. When the same data gets sent to the database, it updates it instead
of creating new useless inserts. This is done by Django's built-in bulk_create
method with the 'ignore_conficts' flag set to true. It also finds an existing
archive, or creates a new archive and uses that key for the FK_archive_set_ID. 
The constraint is on these columns:

   * Session ID (FK_session_id)
   * x Decimal(8,2) - formerly a float
   * y Decimal(8,2) - formerly a float
   * z Decimal(8,2) - formerly a float

B. Restoring annotations

1. This occurs when the user checks one and only one checkbox on the archive page. After
selecting a checkbox, the user chooses the 'Restore the selected archive' option from
the dropdown menu. Once the user clicks 'Go', these events take place:

    #. Get requested archive (set of points in the annotations_points_archive table)
    #. Mark session inactive that is in the archive
    #. Create a new active session and add it to either marked_cell, polygon_sequence or structureCOM
"""

from django.http import Http404
import numpy as np
from statistics import mode
from neuroglancer.models import AnnotationSession,  AnnotationPointArchive, ArchiveSet, BrainRegion, \
    PolygonSequence, StructureCom, PolygonSequence, MarkedCell, UrlModel, get_region_from_abbreviation
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.atlas import get_scales
from neuroglancer.models import CellType, UNMARKED
from neuroglancer.annotation_layer import AnnotationLayer, Annotation
from neuroglancer.annotation_base import AnnotationBase

class AnnotationManager(AnnotationBase):
    """This class handles the management of annotations into the three tables: 

    #. MarkedCells
    #. StructureCOM
    #. PolygonSequence
    """

    def __init__(self, neuroglancerModel):
        """iniatiate the class starting from a perticular url

        Args:
            neuroglancerModel (UrlModel): query result from the django ORM of the neuroglancer_url table
        """
        self.debug = True
        self.neuroglancer_model = neuroglancerModel
        self.owner_id = neuroglancerModel.owner.id
        self.MODELS = ['MarkedCell', 'PolygonSequence', 'StructureCom']
        self.set_annotator_from_id(neuroglancerModel.owner.id)
        self.set_animal_from_id(neuroglancerModel.animal)
        self.scale_xy, self.z_scale = get_scales(self.animal.prep_id)
        self.scales = np.array([self.scale_xy, self.scale_xy, self.z_scale])
        self.batch_size = 50
        self.bulk_mgr = BulkCreateManager(chunk_size=self.batch_size)

    def set_current_layer(self, state_layer):
        """set the current layer attribute from a layer component of neuroglancer json state.
           The incoming neuroglancer json state is parsed by a custom class named AnnotationLayer that 
           groups points according to it's membership to a polygon seqence or volume

        
        :param state_layer (dict): neuroglancer json state component of an annotation layer in dictionary form
        """
        assert 'name' in state_layer
        self.label = str(state_layer['name']).strip()
        self.current_layer = AnnotationLayer(state_layer)


    def archive_and_insert_annotations(self):
        """The main function that updates the database with annotations in the current_layer 
        attribute. This function loops each annotation in the current layer and 
        inserts data into the bulk manager. At the end of the loop, all data is in the bulk
        manager and it gets inserted. We also save the session to update the updated column.
        """
        session = None

        if self.animal is None or self.annotator is None:
            raise Http404

        marked_cells = []
        for annotationi in self.current_layer.annotations:
            # marked cells are treated differently than com, polygon and volume
            if annotationi.is_cell():
                marked_cells.append(annotationi)

            if annotationi.is_com():
                brain_region = get_region_from_abbreviation(annotationi.get_description())
                session = self.get_session(brain_region=brain_region, annotation_type='STRUCTURE_COM')
                self.add_com(annotationi, session)
            if annotationi.is_polygon():
                brain_region = get_region_from_abbreviation('polygon')
                session = self.get_session(brain_region=brain_region, annotation_type='POLYGON_SEQUENCE')
                self.add_polygons(annotationi, session)
            if annotationi.is_volume():
                brain_region = get_region_from_abbreviation(annotationi.get_description())
                session = self.get_session(brain_region=brain_region, annotation_type='POLYGON_SEQUENCE')
                self.add_volumes(annotationi, session)

        if len(marked_cells) > 0:
            batch = []
            marked_cells = np.array(marked_cells)
            description_and_cell_types = np.array([f'{i.description}@{i.category}' for i in marked_cells])
            unique_description_and_cell_types = np.unique(description_and_cell_types)
            brain_region = get_region_from_abbreviation('point')
            for description_cell_type in unique_description_and_cell_types:
                in_category = description_and_cell_types == description_cell_type
                cells = marked_cells[in_category]
                _, cell_type = description_cell_type.split('@')
                if cells[0].description =='positive':
                    source = 'HUMAN_POSITIVE'
                elif cells[0].description =='negative':
                    source = 'HUMAN_NEGATIVE'
                else:
                    source = UNMARKED
                
                session = self.get_session(brain_region=brain_region,
                                               annotation_type='MARKED_CELL', cell_type=cell_type, 
                                               source=source)
                for annotationi in cells:
                    if cell_type == UNMARKED:
                        brain_region = get_region_from_abbreviation('point')
                        marked_cell = self.create_marked_cell(annotationi, session, None, source)
                    else:
                        cell_type = CellType.objects.filter(
                            cell_type=cell_type).first()
                        if cell_type is not None:
                            brain_region = get_region_from_abbreviation('point')
                            marked_cell = self.create_marked_cell(annotationi, session, cell_type, source)
                    
                    batch.append(marked_cell)
            MarkedCell.objects.bulk_create(batch, self.batch_size, ignore_conflicts=True)

        if session is not None:
            session.neuroglancer_model = self.neuroglancer_model
            session.save()
        self.bulk_mgr.done()

    def is_structure_com(self, annotationi: Annotation):
        """Determines if a point annotation is a structure COM.
        A point annotation is a COM if the description corresponds to a structure 
        existing in the database.
        
        :param annotationi (Annotation): the annotation object 
        :return boolean: True or False
        """

        assert annotationi.is_point()
        description = annotationi.get_description()
        if description is not None:
            description = str(description).replace('\n', '').strip()
            return bool(BrainRegion.objects.filter(abbreviation=description).first())
        else:
            return False

    def archive_annotations(self, annotation_session: AnnotationSession):
        """Move the existing annotations into the archive. First, we get the existing
        rows and then we insert those into the archive table. This is a background
        task.
        
        :param annotation_session: annotation session object
        """
        data_model = annotation_session.get_session_model()
        rows = data_model.objects.filter(
            annotation_session__id=annotation_session.id)
        field_names = [
            f.name for f in data_model._meta.get_fields() if not f.name == 'id']
        if rows is not None and len(rows) > 0:
            batch = []
            for row in rows:
                fields = [getattr(row, field_name) for field_name in field_names if hasattr(row, field_name)]
                input = dict(zip(field_names, fields))
                input['archive'] = self.get_archive(annotation_session)
                batch.append(AnnotationPointArchive(**input))
            AnnotationPointArchive.objects.bulk_create(batch, self.batch_size, ignore_conflicts=True)

    def add_com(self, annotationi: Annotation, annotation_session: AnnotationSession):
        """Helper method to add a COM to the bulk manager.

        :param annotationi: A COM annotation
        :param annotation_session: session object
        """
        x, y, z = np.floor(annotationi.coord) * self.scales
        self.bulk_mgr.add(StructureCom(annotation_session=annotation_session,
                                       source='MANUAL', x=x, y=y, z=z))

    def create_marked_cell(self, annotationi: Annotation, annotation_session: AnnotationSession, 
        cell_type, source) -> MarkedCell:
        """Helper method to create a MarkedCell object.

        :param annotationi: A COM annotation
        :param annotation_session: session object
        :param cell_type: the cell type of the marked cell
        :param source: the MARKED/UNMARKED source
        :return: MarkedCell object
        """

        x, y, z = np.floor(annotationi.coord) * self.scales
        return MarkedCell(annotation_session=annotation_session,
                          source=source, x=x, y=y, z=z, cell_type=cell_type)

    def add_polygons(self, annotationi: Annotation, annotation_session: AnnotationSession):
        """Helper method to add a polygon to the bulk manager.

        :param annotationi: A polygon annotation
        :param annotation_session: session object
        """

        z = mode([int(np.floor(pointi.coord_start[2]) * self.z_scale)
                 for pointi in annotationi.childs])
        ordering = 1
        for pointi in annotationi.childs:
            xa, ya, _ = pointi.coord_start * self.scales
            self.bulk_mgr.add(PolygonSequence(annotation_session=annotation_session,
                              x=xa, y=ya, z=z, point_order=ordering, polygon_index=1))
            ordering += 1

    def add_volumes(self, annotationi: Annotation, annotation_session: AnnotationSession):
        """Helper method to add a volume to the bulk manager.

        :param annotationi: A COM annotation
        :param annotation_session: session object
        """

        polygon_index = 1
        for polygoni in annotationi.childs:
            ordering = 1
            z = mode([int(np.floor(coord.coord_start[2]) * self.z_scale)
                     for coord in polygoni.childs])
            for childi in polygoni.childs:
                xa, ya, _ = childi.coord_start * self.scales
                self.bulk_mgr.add(PolygonSequence(annotation_session=annotation_session,
                                                  x=xa, y=ya, z=z, point_order=ordering, polygon_index=polygon_index))
                ordering += 1
            polygon_index += 1


    def get_session(self, brain_region, annotation_type, 
            cell_type = None, source = None):
        """Gets either the existing session or creates a new one.
        We first try by trying to get the exact UrlModel (AKA, neuroglancer state). 
        If that doesn't succeed, we try without the state ID

        :param brain_region: brain region object AKA structure
        :param annotation_type: either marked cell or polygon or COM
        :param source: the MARKED/UNMARKED source
        """

        annotation_session = AnnotationSession.objects.filter(active=True)\
            .filter(annotation_type=annotation_type)\
            .filter(animal=self.animal)\
            .filter(neuroglancer_model=self.neuroglancer_model)\
            .filter(brain_region=brain_region)\
            .filter(annotator=self.annotator)\
            .order_by('-created').first()
            
        if annotation_session is None:
            annotation_session = AnnotationSession.objects.filter(active=True)\
                .filter(annotation_type=annotation_type)\
                .filter(animal=self.animal)\
                .filter(brain_region=brain_region)\
                .filter(annotator=self.annotator)\
                .order_by('-created').first()

        if annotation_session is None:
            annotation_session = self.create_new_session(brain_region, annotation_type)
        else:
            self.archive_annotations(annotation_session)
            
        return annotation_session

    def create_new_session(self, brain_region: BrainRegion, annotation_type: str):
        """Helper method to create a new annotation_session
        
        :param brain_region: brain region object AKA structure
        :param annotation_type: either marked cell or polygon or COM
        """

        annotation_session = AnnotationSession.objects.create(
            animal=self.animal,
            neuroglancer_model=self.neuroglancer_model,
            brain_region=brain_region,
            annotator=self.annotator,
            annotation_type=annotation_type, 
            active=True)
        return annotation_session


    def get_archive(self, annotation_session):
        """Gets either the existing archive or creates a new one.

        :param annotation_session: session object
        """

        queryset = ArchiveSet.objects.filter(active=True)\
            .filter(annotation_session=annotation_session)\

        if len(queryset) == 1:
            archive = queryset[0]
        else:
            archive = self.create_new_archive(annotation_session)
            
        return archive

    def create_new_archive(self, annotation_session):
        """Helper method to create a new session
        
        :param annotation_session: session object
        """

        archive = ArchiveSet.objects.create(annotation_session=annotation_session, active=True)
        return archive
