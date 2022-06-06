import numpy as np
from statistics import mode
from neuroglancer.models import AnnotationSession,  AnnotationPointArchive, BrainRegion, \
    PolygonSequence, StructureCom, PolygonSequence, MarkedCell, get_region_from_abbreviation
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.atlas import get_scales
from neuroglancer.models import CellType
from abakit.lib.annotation_layer import AnnotationLayer, Annotation
from neuroglancer.AnnotationBase import AnnotationBase


class AnnotationManager(AnnotationBase):
    '''This class handles the inseration of annotations into the three tables: MarkedCells, StructureCOM and PolygonSequence'''

    def __init__(self, neuroglancerModel):
        """iniatiate the class starting from a perticular url

        Args:
            neuroglancerModel (UrlModel): query result from the django ORM of the neuroglancer_url table
        """
        self.debug = True
        self.neuroglancer_state = neuroglancerModel.url
        self.owner_id = neuroglancerModel.owner.id
        self.MODELS = ['MarkedCell', 'PolygonSequence', 'StructureCom']
        self.set_annotator_from_id(neuroglancerModel.owner.id)
        self.set_animal_from_id(neuroglancerModel.animal)
        self.scale_xy, self.z_scale = get_scales(self.animal.prep_id)
        self.scales = np.array([self.scale_xy, self.scale_xy, self.z_scale])
        self.bulk_mgr = BulkCreateManager(chunk_size=100)

    def set_current_layer(self, state_layer):
        """set the current layer attribute from a layer component of neuroglancer json state.
           The incoming neuroglancer json state is parsed by abakit custom class named AnnotationLayer that 
           groups points according to it's membership to a polygon seqence or volume

        Args:
            state_layer (dict): neuroglancer json state component of an annotation layer in dictionary form
        """
        assert 'name' in state_layer
        self.label = str(state_layer['name']).strip()
        self.current_layer = AnnotationLayer(state_layer)

    def update_data_in_current_layer(self):
        """Update the databse with the annotations in the current layer
           This moves the old annotations to the archive, set old sessions 
           as inactive and inserts the new annotation points.
           The main function archive_and_insert_annotations runs either directly 
           or in the background depending if the debug option is selected
        """
        if self.animal is not None and self.annotator is not None:
            if self.debug:
                self.archive_and_insert_annotations()
            else:
                self.archive_and_insert_annotations(
                    verbose_name="Bulk annotation move and insert",  creator=self.annotator)

    def update_annotation_data(self):
        """
        This method goes through all the annotation layer in a neuroglancer state and update the database entries.
        Currently this is not being used
        """
        if 'layers' in self.neuroglancer_state:
            state_layers = self.neuroglancer_state['layers']
            for state_layer in state_layers:
                if 'annotations' in state_layer:
                    self.set_current_layer(state_layer)
                    self.update_data_in_current_layer()


    def archive_and_insert_annotations(self):
        """The main function that updates the database with annotations in the current_layer attribute
           This function loops each annotation in the curent layer and inserts/archive points in the 
           appropriate table
        """
        marked_cells = []
        for annotationi in self.current_layer.annotations:
            if annotationi.is_com():
                brain_region = get_region_from_abbreviation(
                    annotationi.get_description())
                new_session = self.get_new_session_and_archive_points(
                    brain_region=brain_region, annotation_type='STRUCTURE_COM')
                self.add_com(annotationi, new_session)
            if annotationi.is_cell():
                marked_cells.append(annotationi)
            if annotationi.is_polygon():
                brain_region = get_region_from_abbreviation('polygon')
                new_session = self.get_new_session_and_archive_points(
                    brain_region=brain_region, annotation_type='POLYGON_SEQUENCE')
                self.add_polygons(annotationi, new_session)
            if annotationi.is_volume():
                brain_region = get_region_from_abbreviation(
                    annotationi.get_description())
                new_session = self.get_new_session_and_archive_points(
                    brain_region=brain_region, annotation_type='POLYGON_SEQUENCE')
                self.add_volumes(annotationi, new_session)
        if len(marked_cells) > 0:
            categories = np.array([i.category for i in marked_cells])
            unique_category = np.unique(categories)
            for category in unique_category:
                in_category = categories == category
                cells = marked_cells[in_category]
                new_session = self.get_new_session_and_archive_points(
                    brain_region=brain_region, annotation_type='MARKED_CELL')
                for annotationi in cells:
                    cell_type = CellType.objects.filter(
                        cell_type=category).first()
                    if cell_type is not None:
                        brain_region = get_region_from_abbreviation('point')
                        self.add_marked_cells(
                            annotationi, new_session, cell_type)
        self.bulk_mgr.done()

    def is_structure_com(self, annotationi: Annotation):
        """ determines if a point annotation is a structure COM
            A point annotation is a COM if the description correspond to a structure existing in the database
        Args:
            annotationi (abakit:Annotation): the annotation object 

        Returns:
            boolean: True or False
        """
        # TODO Nage implemented changes in neuroglancer that explicitly distinguish between marked cells and COMs.  
        # Code change that utilize those
        # markings will identify the two categories in a more robust manner
        assert annotationi.is_point()
        description = annotationi.get_description()
        if description is not None:
            description = str(description).replace('\n', '').strip()
            return bool(BrainRegion.objects.filter(abbreviation=description).first())
        else:
            return False

    def get_parent_id_for_current_session_and_achrive_points(self, annotation_session):
        """archives the points related to an annotation session and returns the if of this session as 
        the parent id of the new session

        Args:
            annotation_session (AnnotationSession): query result from django ORM AnnotationSession.
            None type is passed to this function if no annotation session current exists for 
            the specified set of points

        Returns:
            int: id of current session it is not none
        """
        if annotation_session is not None:
            self.archive_annotations(annotation_session)
            parent = annotation_session.id
        else:
            parent = 0
        return parent

    def get_new_session_and_archive_points(self, brain_region, annotation_type):
        """ This function does the following according to two scenarios 
            Scenario1:
               the session type specified by the group of points in question does not exist in the database
               then:
               a new session is created with parent id 0 
            Scenario2:
               The session type specified do exist
               then:
               the points corresponding to the current session is moved to the

        Args:
            brain_region (_type_): _description_
            annotation_type (_type_): _description_

        Returns:
            _type_: _description_
        """
        annotation_session = self.get_existing_session(
            brain_region=brain_region, annotation_type=annotation_type)
        if annotation_session is not None:
            parent_id = self.get_parent_id_for_current_session_and_achrive_points(
                annotation_session)
            annotation_session.active = 0
            annotation_session.save()
        else:
            parent_id = 0
        new_session = self.create_new_session(
            brain_region=brain_region, annotation_type=annotation_type, parent=parent_id)
        return new_session

    def archive_annotations(self, annotation_session: AnnotationSession):
        '''
        Move existing annotations into the archive. First we get the existing
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
        '''
        data_model = annotation_session.get_session_model()
        rows = data_model.objects.filter(
            annotation_session__id=annotation_session.id)
        field_names = [
            f.name for f in data_model._meta.get_fields() if not f.name == 'id']
        if rows is not None and len(rows) > 0:
            for row in rows:
                fields = [getattr(row, namei) for namei in field_names]
                input = dict(zip(field_names, fields))
                self.bulk_mgr.add(AnnotationPointArchive(**input))
        self.bulk_mgr.done()
        rows.delete()

    def add_com(self, annotationi: Annotation, annotation_session: AnnotationSession):
        x, y, z = np.floor(annotationi.coord) * self.scales
        self.bulk_mgr.add(StructureCom(annotation_session=annotation_session,
                                       source='MANUAL', x=x, y=y, z=z))

    def add_marked_cells(self, annotationi: Annotation, annotation_session: AnnotationSession, cell_type):
        x, y, z = np.floor(annotationi.coord) * self.scales
        self.bulk_mgr.add(MarkedCell(annotation_session=annotation_session,
                          source='HUMAN-POSITIVE', x=x, y=y, z=z, cell_type=cell_type))

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

    def get_existing_session(self, brain_region: BrainRegion, annotation_type):
        return AnnotationSession.objects.filter(animal=self.animal)\
                                        .filter(brain_region=brain_region)\
                                        .filter(annotator=self.annotator)\
                                        .filter(annotation_type=annotation_type).first()

    def create_new_session(self, brain_region: BrainRegion, annotation_type, parent=0):
        annotation_session = AnnotationSession.objects.create(
            animal=self.animal,
            brain_region=brain_region,
            annotator=self.annotator,
            annotation_type=annotation_type, parent=parent)
        return annotation_session
