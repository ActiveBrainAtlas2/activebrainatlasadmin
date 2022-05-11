import numpy as np
from statistics import mode
from django.contrib.auth.models import User
from django.http import Http404
from neuroglancer.models import  AnnotationPoints, AnnotationPointArchive, \
    ArchiveSet, BrainRegion, InputType
from brain.models import Animal
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.atlas import get_scales
from neuroglancer.models import MANUAL, POINT_ID, POLYGON_ID
from abakit.lib.annotation_layer import AnnotationLayer
from background_task import background
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

from timeit import default_timer as timer


def update_annotation_data(neuroglancerModel):
    """
    This is the method from the create and update methods
    in the neuroglancer state serializer. It will spawn off the 
    SQL insert intensive bits to the background.
    """    
    json_txt = neuroglancerModel.url
    owner_id = neuroglancerModel.owner.id

    try:
        loggedInUser = User.objects.get(pk=neuroglancerModel.owner.id)
    except User.DoesNotExist:
        logger.error("User does not exist")
        return
    try:
        animal = Animal.objects.get(pk=neuroglancerModel.animal)
    except Animal.DoesNotExist:
        logger.error("Animal does not exist")
        return
    if 'layers' in json_txt:
        state_layers = json_txt['layers']
        for state_layer in state_layers:
            if 'annotations' in state_layer:
                label = str(state_layer['name']).strip()
                if animal is not None and loggedInUser is not None and \
                    not 'annotation' in label:
                    inactivate_annotations(animal, label)
                    # move_and_insert_annotations(animal.prep_id, state_layer, owner_id, label, verbose_name="Bulk annotation move and insert",  creator=loggedInUser)
                    # Do not remove these comments.
                    # Uncomment the line below for testing and comment out the line above and the @background
                    # decorator
                    move_and_insert_annotations(animal.prep_id, state_layer, owner_id, label)


def inactivate_annotations(animal, label):
    """
    Update the existing annotations that are manual, prep, active 
    set them to inactive. Updates are fast, so this does not 
    need to be backgrounded. In fact, it really needs to be done right away.
    """
    AnnotationPoints.objects.filter(input_type_id=MANUAL)\
    .filter(animal=animal)\
    .filter(active=True)\
    .filter(label=label)\
    .update(active=False)


# @background(schedule=0)
def move_and_insert_annotations(prep_id, layer, owner_id, label):
    '''
    This is a simple method that just calls two other methods.
    The reason for this method's existence is just to make sure the CPU/time
    instensive methods are run in the proper order and are run in the background.
    :param prep_id: char string of the animal name
    :param layer: json layer data
    :param owner_id: int of the auth user primary key
    :param label: char string of the name of the layer
    '''
    move_annotations(prep_id, owner_id, label)
    bulk_annotations(prep_id, layer, owner_id, label)


@background(schedule=0)
def restore_annotations(archive_id, prep_id, label):
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
        archive = ArchiveSet.objects.get(pk=archive_id)
    except ArchiveSet.DoesNotExist:
        print('No archive to fetch')
        raise Http404
    
    AnnotationPoints.objects.filter(input_type_id=MANUAL)\
    .filter(animal__prep_id=prep_id)\
    .filter(active=True)\
    .filter(label=label)\
    .update(active=False)

    rows = AnnotationPointArchive.objects.filter(archive=archive)
    bulk_mgr = BulkCreateManager(chunk_size=100)
    for row in rows:
        bulk_mgr.add(AnnotationPoints(animal=row.animal, brain_region=row.brain_region,
            label=row.label, polygon_id=row.polygon_id, owner=row.owner, input_type=row.input_type,
            x=row.x, y=row.y, z=row.z))
    bulk_mgr.done()
    
    # now delete the existing inactivated rows
    AnnotationPoints.objects.filter(input_type_id=MANUAL)\
    .filter(animal__prep_id=prep_id)\
    .filter(active=False)\
    .filter(label=label)\
    .delete()

    
def move_annotations(prep_id, owner_id, label):
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
    # animal
    try:
        animal = Animal.objects.get(pk=prep_id)
    except Animal.DoesNotExist:
        logger.error("Animal does not exist")
        print("Animal does not exist")
        return
    # logged in user, updatedBy
    try:
        loggedInUser = User.objects.get(pk=owner_id)
    except User.DoesNotExist:
        logger.error("User does not exist")
        print("User does not exist")
        return
    
    '''
    First, we need to check if there is any existing data in the 
    non-archive online table. If there are, we create an archive,
    otherwise, you can't archive None!
    
    Then, we check if there is an existing dataset of the same data in the 
    annotation point archive. If so, we get that archive ID and
    that then is the parent ID for the new archive set.
    '''
    start = timer()
    parent = 0
    # check online table
    rows = AnnotationPoints.objects.filter(input_type__id=MANUAL)\
        .filter(animal=animal)\
        .filter(label=label).filter(owner=loggedInUser)
        
    if rows is not None and len(rows) > 0: 
        # now check the point archive table
        try:
            query_set = AnnotationPointArchive.objects\
                .filter(animal=animal)\
                .filter(label=label)\
                .filter(input_type_id=MANUAL)\
                .order_by('-id')
        except AnnotationPointArchive.DoesNotExist:
            parent = 0
        if query_set is not None and len(query_set) > 0:
            annotationPointArchive = query_set[0]
            try:
                parent = annotationPointArchive.archive.id
            except ArchiveSet.DoesNotExist:
                parent = 0
        input_type = InputType.objects.get(pk=MANUAL)
        archive = ArchiveSet.objects.create(parent=parent,
                                            animal=animal,
                                            input_type=input_type,
                                            label=label,
                                            updatedby=loggedInUser)
        
    bulk_mgr = BulkCreateManager(chunk_size=100)
    for row in rows:
        bulk_mgr.add(AnnotationPointArchive(animal=row.animal, brain_region=row.brain_region,
            label=row.label, polygon_id=row.polygon_id, owner=row.owner, input_type=row.input_type, volume_id=row.volume_id,
            x=row.x, y=row.y, z=row.z, archive=archive, ordering=row.ordering))
    bulk_mgr.done()
    print(f'{len(rows)} rows deleted')
    rows.delete()
    end = timer()
    # print(f'Bulk move took {end - start} seconds') 


def bulk_annotations(prep_id, layer, owner_id, label):
    start = timer()
    try:
        loggedInUser = User.objects.get(pk=owner_id)
    except User.DoesNotExist:
        logger.error("bulk_annoations User does not exist")
        print('bulk_annoations User does not exist')
        return
    try:
        animal = Animal.objects.get(pk=prep_id)
    except Animal.DoesNotExist:
        print("bulk_annoations Animal does not exist")
        return
    bulk_mgr = BulkCreateManager(chunk_size=100)
    scale_xy, z_scale = get_scales(prep_id)
    scales = np.array([scale_xy, scale_xy, z_scale])
    polygon_structure = BrainRegion.objects.get(pk=POLYGON_ID)
    layer = AnnotationLayer(layer)
    for annotation in layer.annotations:
        if annotation._type == 'point':
            x, y, z = annotation.coord * scales
            z = np.floor(z)
            brain_region = get_brain_region(annotation)
            if brain_region is not None:
                bulk_mgr.add(AnnotationPoints(animal=animal, brain_region=brain_region,
                label=label, active=True, owner=loggedInUser, input_type_id=MANUAL,
                ordering=0,
                x=x, y=y, z=z))
        if annotation._type == 'polygon':
            polygon_id = annotation.id
            z = mode([ int(np.floor(pointi.coord_start[2]) * z_scale) for pointi in annotation.childs])
            ordering = 1
            for pointi in annotation.childs:
                xa, ya, _ = pointi.coord_start * scales
                bulk_mgr.add(AnnotationPoints(animal=animal, brain_region=polygon_structure,
                owner=loggedInUser, active=True, input_type_id=MANUAL, label=label, polygon_id=polygon_id,
                x=xa, y=ya, z=z, ordering=ordering))
                ordering += 1
        if annotation._type == 'volume':
            volume_label = annotation.description
            move_annotations(prep_id, owner_id, volume_label)
            volume_id = annotation.id
            for polygoni in annotation.childs:
                polygon_id = polygoni.id
                z = mode([ int(np.floor(coord.coord_start[2]) * z_scale) for coord in polygoni.childs])
                ordering = 1
                for childi in polygoni.childs:
                    xa, ya, _ = childi.coord_start * scales
                    bulk_mgr.add(AnnotationPoints(animal=animal, brain_region=polygon_structure,
                    owner=loggedInUser, active=True, input_type_id=MANUAL, label=volume_label, polygon_id=polygon_id,
                    volume_id=volume_id, x=xa, y=ya, z=z, ordering=ordering))
                    ordering += 1
    bulk_mgr.done()
    end = timer()
    # print(f'Bulk insert took {end - start} seconds') 


def get_brain_region(annotation):
    '''
    This method is important! By default, the brain regions is just an annotation
    point. But, it could also be a region drawn by an anatomist (polygon) or
    it could be one of the atlas structures.
    :param annotation:
    '''
    brain_region = BrainRegion.objects.get(pk=POINT_ID)
    if hasattr(annotation, 'description'):
        abbreviation = str(annotation.description).replace('\n', '').strip()
        try:
            query_set = BrainRegion.objects.filter(abbreviation=abbreviation)
        except BrainRegion.DoesNotExist:
            logger.error(f'BrainRegion {abbreviation} does not exist')
        if query_set is not None and len(query_set) > 0:
            brain_region = query_set[0]
    return brain_region
