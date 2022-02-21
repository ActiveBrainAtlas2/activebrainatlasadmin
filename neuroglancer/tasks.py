from django.contrib.auth.models import User
import datetime
from neuroglancer.models import BrainRegion, AnnotationPoints, AnnotationPointArchive
from brain.models import Animal
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.atlas import get_scales
from timeit import default_timer as timer
from math import isclose
from background_task import background

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
MANUAL = 1
CORRECTED = 2
LINE = 5
POINT_ID = 52
LINE_ID = 53

def update_annotation_data(neuroglancerModel):
    """
    This is the method from brainsharer_portal. It will spawn off the 
    SQL insert intensive bits to the background.
    """    
    start = timer()
    json_txt = neuroglancerModel.url
    try:
        loggedInUser = User.objects.get(pk=neuroglancerModel.person.id)
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
                    label != 'annotation':
                    inactivate_annotations(animal, label)
                    move_annotations(animal, label)
                    bulk_annotations(neuroglancerModel.animal, state_layer, 
                                     neuroglancerModel.person.id, label, 
                                     verbose_name="Bulk annotation insert", 
                                     creator=loggedInUser)
                
    end = timer()
    print(f'Updating all annotations took {end - start} seconds')


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

@background(schedule=0)
def move_annotations(prep_id, label):
    '''
    Move existing annotations into the archive. First we get the existing
    rows and then we insert those into the archive table. This is rather
    expensive operation to perform as we're doing:
        1. a select of the existing rows.
        2. bulk inserts of those rows
        3. deleting those rows from the primary table
    :param animal: animal object
    :param label: char of label name
    TODO, we need to get the FK from the archive table, insert
    an appropriate parent in archive_set
    '''    
    try:
        animal = Animal.objects.get(pk=prep_id)
    except Animal.DoesNotExist:
        logger.error("Animal does not exist")
        return
    rows = AnnotationPoints.objects.filter(input_type__id=MANUAL)\
        .filter(animal=animal)\
        .filter(label=label)
        
    bulk_mgr = BulkCreateManager(chunk_size=100)
    for row in rows:
        bulk_mgr.add(AnnotationPointArchive(animal=row.animal, brain_region=row.brain_region,
            label=row.label, owner=row.owner, input_type=row.input_type,
            x=row.x, y=row.y, z=row.z))
    bulk_mgr.done()
    # now delete them as they are no longer useful in the original table.
    rows.delete()


@background(schedule=10)
def bulk_annotations(prep_id, layer, person_id, label):
    start = timer()
    try:
        loggedInUser = User.objects.get(pk=person_id)
    except User.DoesNotExist:
        logger.error("User does not exist")
        return
    try:
        animal = Animal.objects.get(pk=prep_id)
    except Animal.DoesNotExist:
        logger.error("Animal does not exist")
        return
    bulk_mgr = BulkCreateManager(chunk_size=100)
    scale_xy, z_scale = get_scales(prep_id)
    annotations = layer['annotations']
    line_structure = BrainRegion.objects.get(pk=LINE_ID)
    for annotation in annotations:
        if 'point' in annotation:
            x1 = annotation['point'][0] * scale_xy
            y1 = annotation['point'][1] * scale_xy
            z1 = annotation['point'][2] * z_scale
            structure = get_structure(annotation)
            if structure is not None:
                bulk_mgr.add(AnnotationPoints(prep=animal, structure=structure,
                label=label, active=True, person=loggedInUser, input_type_id=MANUAL,
                x=x1, y=y1, section=z1))
        if 'parentAnnotationId' in annotation and 'pointA' in annotation and 'pointB' in annotation:
            xa = annotation['pointA'][0] * scale_xy
            ya = annotation['pointA'][1] * scale_xy
            za = annotation['pointA'][2] * z_scale
            
            xb = annotation['pointB'][0] * scale_xy
            yb = annotation['pointB'][1] * scale_xy
            zb = annotation['pointB'][2] * z_scale
            bulk_mgr.add(AnnotationPoints(prep=animal, structure=line_structure, created=datetime.datetime.now(),
            label=label, person=loggedInUser, input_type_id=LINE,
            x=xa, y=ya, section=za))
            if not isclose(xa, xb, rel_tol=1e-0) and not isclose(ya, yb, rel_tol=1e-0):
                print('adding', xa, xb)
                bulk_mgr.add(AnnotationPoints(prep=animal, structure=line_structure, created=datetime.datetime.now(),
                label=label, person=loggedInUser, input_type_id=LINE,
                x=xb, y=yb, section=zb))
    bulk_mgr.done()
    end = timer()
    print(f'Inserting {layer_name} annotations took {end - start} seconds')


def get_structure(annotation):
    structure = BrainRegion.objects.get(pk=POINT_ID)
    if 'description' in annotation:
        abbreviation = str(annotation['description']).replace('\n', '').strip()
        try:
            structure = BrainRegion.objects.get(abbreviation=abbreviation)
        except BrainRegion.DoesNotExist:
            logger.error(f'BrainRegion {abbreviation} does not exist')
    return structure
