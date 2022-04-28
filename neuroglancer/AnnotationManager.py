from attr import has
import numpy as np
from statistics import mode
from django.contrib.auth.models import User
from django.http import Http404
from django.apps import apps
from neuroglancer.models import AnnotationSession,  AnnotationPointArchive, BrainRegion, PolygonSequence,StructureCom,PolygonSequence,MarkedCell
from brain.models import Animal
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.atlas import get_scales
from neuroglancer.models import MANUAL, POINT_ID, POLYGON_ID
from abakit.lib.annotation_layer import AnnotationLayer
from background_task import background
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

class AnnotationManager:
    def __init__(self,neuroglancerModel):
        self.debug = True
        self.neuroglancer_state = neuroglancerModel.url
        self.owner_id = neuroglancerModel.owner.id
        self.MODELS = ['MarkedCell','PolygonSequence','StructureCom']
        try:
            self.loggedInUser = User.objects.get(pk=neuroglancerModel.owner.id)
        except User.DoesNotExist:
            logger.error("User does not exist")
            return
        try:
            self.animal = Animal.objects.get(pk=neuroglancerModel.animal)
        except Animal.DoesNotExist:
            logger.error("Animal does not exist")
            return
        self.scale_xy, self.z_scale = get_scales(self.animal.prep_id)
        self.scales = np.array([self.scale_xy, self.scale_xy, self.z_scale])
        self.bulk_mgr = BulkCreateManager(chunk_size=100)

    def set_current_layer(self,state_layer):
        assert hasattr(state_layer,'name')
        self.label = str(state_layer['name']).strip()
        self.current_layer = AnnotationLayer(state_layer)
    
    def update_data_in_current_layer(self):
        if self.animal is not None and self.loggedInUser is not None:
            if self.debug:
                self.archive_and_insert_annotations()
            else:
                self.archive_and_insert_annotations(verbose_name="Bulk annotation move and insert",  creator=self.loggedInUser)

    def update_annotation_data(self):
        """
        This is the method from the create and update methods
        in the neuroglancer state serializer. It will spawn off the 
        SQL insert intensive bits to the background.
        """    
        if 'layers' in self.neuroglancer_state:
            state_layers = self.neuroglancer_state['layers']
            for state_layer in state_layers:
                if 'annotations' in state_layer:
                    self.set_current_layer(state_layer)
                    self.update_data_in_current_layer()


    # @background(schedule=0)
    def archive_and_insert_annotations(self, label):
        '''
        This is a simple method that just calls two other methods.
        The reason for this method's existence is just to make sure the CPU/time
        instensive methods are run in the proper order and are run in the background.
        :param prep_id: char string of the animal name
        :param layer: json layer data
        :param owner_id: int of the auth user primary key
        :param label: char string of the name of the layer
        '''
        for annotationi in self.current_layer.annotations:
            if annotationi.is_point():
                marked_cells = []
                if self.is_structure_com(annotationi):
                    brain_region = self.get_brain_region(annotationi.get_description())
                    new_session = self.get_new_session_and_archive_points(brain_region=brain_region,annotation_type='STRUCTURE_COM')
                    self.add_com(annotationi,new_session)
                else:
                    marked_cells.append(annotationi)
                    self.add_marked_cells(marked_cells)
            if annotationi.is_polygon():
                brain_region = self.get_brain_region('polygon')
                new_session = self.get_new_session_and_archive_points(brain_region=brain_region,annotation_type='POLYGON_SEQUENCE')
                self.add_polygons(annotationi,new_session)
            if annotationi.is_volume():
                brain_region = self.get_brain_region(annotationi.get_description())
                new_session = self.get_new_session_and_archive_points(brain_region=brain_region,annotation_type='POLYGON_SEQUENCE')
                self.add_volumes(annotationi,new_session)
            if len(marked_cells)>0:
                brain_region = self.get_brain_region('point')
                new_session = self.get_new_session_and_archive_points(brain_region=brain_region,annotation_type='MARKED_CELL')
                self.add_volumes(annotationi,new_session)
        self.bulk_mgr.done()
    
    def is_structure_com(self,annotationi):
        assert annotationi.is_point()
        description = annotationi.get_description()
        if description is not None:
            description = str(description).replace('\n', '').strip()
            return bool(BrainRegion.objects.filter(abbreviation=description).first())
        else:
            return False

    def get_parent_id_for_current_session_and_achrive_points(self,session):
        if session is not None:
            self.archive_annotations(session)
            parent=session.id
        else:
            parent = 0
        return parent
    
    def get_new_session_and_archive_points(self,brain_region,annotation_type):
        session = self.get_existing_session(brain_region=brain_region,annotation_type=annotation_type)
        parent = self.get_parent_id_for_current_session_and_achrive_points(session)
        new_session = self.create_new_session(brain_region=brain_region,annotation_type=annotation_type,parent=parent)
        return new_session
        
    def archive_annotations(self,session:AnnotationSession):
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
        data_model = session.get_session_model()
        rows = data_model.objects.filter(annotation_session__id=session.id)    
        field_names = [f.name for f in data_model._meta.get_fields() if not f.name =='active']
        if rows is not None and len(rows) > 0: 
            for row in rows:
                fields = [getattr(row,namei) for namei in field_names]
                input = dict(zip(field_names,fields))
                self.bulk_mgr.add(AnnotationPointArchive(**input,active = 0))
        self.bulk_mgr.done()
        rows.delete()

    def add_com(self,annotationi,session):
        x, y, z = annotationi.coord * self.scales
        self.bulk_mgr.add(StructureCom(annotation_session=session,
                        source='MANUAL', x=x, y=y, z=z))
    
    def add_marked_cells(self,annotationi,session,label):
        x, y, z = annotationi.coord * self.scales
        self.bulk_mgr.add(MarkedCell(annotation_session=session,
                        label=label, x=x, y=y, z=z))
    
    def add_polygons(self,annotationi,session):
        z = mode([ int(np.floor(pointi.coord_start[2]) * self.z_scale) for pointi in annotationi.childs])
        ordering = 1
        for pointi in annotationi.childs:
            xa, ya, _ = pointi.coord_start * self.scales
            self.bulk_mgr.add(PolygonSequence(annotation_session=session,x=xa, y=ya, z=z, point_order=ordering, polygon_index=1))
            ordering+=1
    
    def add_volumes(self,annotationi,session):
        polygon_index = 1
        for polygoni in annotationi.childs:
            ordering = 1
            z = mode([ int(np.floor(coord.coord_start[2]) * self.z_scale) for coord in polygoni.childs])
            for childi in polygoni.childs:
                xa, ya, _ = childi.coord_start * self.scales
                self.bulk_mgr.add(PolygonSequence(annotation_session=session,
                                                    x=xa, y=ya, z=z, point_order=ordering, polygon_index=polygon_index))
                ordering += 1
            polygon_index+=1

    def get_existing_session(self,brain_region:BrainRegion,annotation_type):
        return AnnotationSession.objects.filter(animal = self.animal)\
                                        .filter(brain_region = brain_region)\
                                        .filter(annotator = self.loggedInUser)\
                                        .filter(annotation_type = annotation_type).first()
    
    def create_new_session(self,brain_region:BrainRegion,annotation_type,parent=0):
        annotation_session = AnnotationSession.objects.create(\
                                animal=self.animal,
                                brain_region=brain_region,
                                annotator=self.loggedInUser,
                                annotation_type=annotation_type,parent = parent)
        return annotation_session
    
@background(schedule=0)
def restore_annotations(session_id):
    '''
        Inactivate the existing annotations that are manual, prep, active.
        It is OK to inactivate them as they must already be in the:
        annotation_points_archive table for this operation to be
        accessible. 
        Fetch rows from the archive and 
        insert into online table
    :archive_id: int of primary key of archive_set
    :param prep_id: char string of animal name
    :param label: char staring of layer name
    '''
    try:
        session = AnnotationSession.objects.get(pk=session_id)
    except AnnotationSession.DoesNotExist:
        print('No session to fetch')
        raise Http404
    data_model = session.get_session_model()
    data_model.objects.filter(annotation_session=session).filter(active=True).delete()
    field_names = [f.name for f in data_model._meta.get_fields() if not f.name =='active']
    rows = AnnotationPointArchive.objects.filter(session=session)
    bulk_mgr = BulkCreateManager(chunk_size=100)
    for row in rows:
        fields = [getattr(row,namei) for namei in field_names]
        input = dict(zip(field_names,fields))
        bulk_mgr.add(data_model(**input,active = 1))
    bulk_mgr.done()