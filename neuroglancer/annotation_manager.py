from django.http import Http404
import numpy as np
from statistics import mode
from neuroglancer.models import AnnotationSession,  AnnotationPointArchive, ArchiveSet, BrainRegion, \
    PolygonSequence, StructureCom, PolygonSequence, MarkedCell, get_region_from_abbreviation
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.atlas import get_scales
from neuroglancer.models import CellType, UNMARKED
from neuroglancer.annotation_layer import AnnotationLayer, Annotation
from neuroglancer.annotation_base import AnnotationBase

class AnnotationManager(AnnotationBase):
    """This class handles the inseration of annotations into the three tables: MarkedCells, StructureCOM and PolygonSequence
    """

    def __init__(self, neuroglancerModel):
        """iniatiate the class starting from a perticular url

        Args:
            neuroglancerModel (UrlModel): query result from the django ORM of the neuroglancer_url table
        """
        self.debug = False
        self.neuroglancer_state = neuroglancerModel.url
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

        Args:
            state_layer (dict): neuroglancer json state component of an annotation layer in dictionary form
        """
        assert 'name' in state_layer
        self.label = str(state_layer['name']).strip()
        self.current_layer = AnnotationLayer(state_layer)


    def archive_and_insert_annotations(self):
        """The main function that updates the database with annotations in the current_layer attribute
           This function loops each annotation in the curent layer and inserts/archive points in the 
           appropriate table
           This: 

            1. Moves the old annotations to the archive 
            2. Sets old sessions as inactive 
            3. Inserts the new annotation points.
        """
        if self.animal is None or self.annotator is None:
            raise Http404

        marked_cells = []
        for annotationi in self.current_layer.annotations:
            if annotationi.is_com():
                brain_region = get_region_from_abbreviation(
                    annotationi.get_description())
                session = self.get_session(brain_region=brain_region, annotation_type='STRUCTURE_COM')
                self.add_com(annotationi, session)
            if annotationi.is_cell():
                marked_cells.append(annotationi)
            if annotationi.is_polygon():
                brain_region = get_region_from_abbreviation('polygon')
                session = self.get_session(brain_region=brain_region, annotation_type='POLYGON_SEQUENCE')
                self.add_polygons(annotationi, session)
            if annotationi.is_volume():
                brain_region = get_region_from_abbreviation(annotationi.get_description())
                session = self.get_session(brain_region=brain_region, annotation_type='POLYGON_SEQUENCE')
                self.add_volumes(annotationi, session)

        if len(marked_cells) > 0:
            marked_cells = np.array(marked_cells)
            description_and_cell_types = np.array([f'{i.description}@{i.category}' for i in marked_cells])
            unique_description_and_cell_types = np.unique(description_and_cell_types)
            brain_region = get_region_from_abbreviation('point')
            for description_cell_type in unique_description_and_cell_types:
                in_category = description_and_cell_types == description_cell_type
                cells = marked_cells[in_category]
                _,cell_type = description_cell_type.split('@')
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
                        self.add_marked_cells(annotationi, session, None, source)
                    else:
                        cell_type = CellType.objects.filter(
                            cell_type=cell_type).first()
                        if cell_type is not None:
                            brain_region = get_region_from_abbreviation('point')
                            self.add_marked_cells(annotationi, session, cell_type, source)
        self.bulk_mgr.done()

    def is_structure_com(self, annotationi: Annotation):
        """ determines if a point annotation is a structure COM
            A point annotation is a COM if the description correspond to a structure 
            existing in the database
        Args:
            annotationi (Annotation): the annotation object 

        Returns:
            boolean: True or False
        """
        # TODO Naga implemented changes in neuroglancer that explicitly distinguish 
        # between marked cells and COMs.  
        # Code change that utilize those
        # markings will identify the two categories in a more robust manner
        assert annotationi.is_point()
        description = annotationi.get_description()
        if description is not None:
            description = str(description).replace('\n', '').strip()
            return bool(BrainRegion.objects.filter(abbreviation=description).first())
        else:
            return False

    def archive_annotations(self, annotation_session: AnnotationSession):
        """Move existing annotations into the archive. First we get the existing
        rows and then we insert those into the archive table. This is a background
        task as we're doing:
        1. a select of the existing rows.
        2. bulk inserts of those rows
        3. deleting those rows from the primary table
        
        :param animal: animal object
        :param label: char of label name
        
        TODO, we need to get the FK from the archive table, insert
        an appropriate parent in archive_set. After we get the animal,
        we need to create an archive
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
        rows.delete()

    def add_com(self, annotationi: Annotation, annotation_session: AnnotationSession):
        x, y, z = np.floor(annotationi.coord) * self.scales
        self.bulk_mgr.add(StructureCom(annotation_session=annotation_session,
                                       source='MANUAL', x=x, y=y, z=z))

    def add_marked_cells(self, annotationi: Annotation, annotation_session: AnnotationSession, 
        cell_type, source):
        x, y, z = np.floor(annotationi.coord) * self.scales
        self.bulk_mgr.add(MarkedCell(annotation_session=annotation_session,
                          source=source, x=x, y=y, z=z, cell_type=cell_type))

    def add_polygons(self, annotationi: Annotation, annotation_session: AnnotationSession):
        z = mode([int(np.floor(pointi.coord_start[2]) * self.z_scale)
                 for pointi in annotationi.childs])
        ordering = 1
        for pointi in annotationi.childs:
            xa, ya, _ = pointi.coord_start * self.scales
            self.bulk_mgr.add(PolygonSequence(annotation_session=annotation_session,
                              x=xa, y=ya, z=z, point_order=ordering, polygon_index=1))
            ordering += 1

    def add_volumes(self, annotationi: Annotation, annotation_session: AnnotationSession):
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
        """

        queryset = AnnotationSession.objects.filter(active=True)\
            .filter(annotation_type=annotation_type)\
                .filter(animal=self.animal)\
                .filter(brain_region=brain_region)\
                .filter(annotator=self.annotator)\
                .order_by('-created').first()

        if len(queryset) == 1:
            session = queryset[0]
            self.archive_annotations(session)

        else:
            session = self.create_new_session(
                brain_region=brain_region, annotation_type=annotation_type)
            
        return session

    def create_new_session(self, brain_region: BrainRegion, annotation_type):
        annotation_session = AnnotationSession.objects.create(
            animal=self.animal,
            brain_region=brain_region,
            annotator=self.annotator,
            annotation_type=annotation_type, 
            active=True)
        return annotation_session


    def get_archive(self, session):
        """Gets either the existing session or creates a new one.
        """

        queryset = ArchiveSet.objects.filter(active=True)\
            .filter(annotation_session=session)\

        if len(queryset) == 1:
            archive = queryset[0]
        else:
            archive = self.create_new_archive(session)
            
        return archive

    def create_new_archive(self, session):
        archive = ArchiveSet.objects.create(annotation_session=session, active=True)
        return archive
