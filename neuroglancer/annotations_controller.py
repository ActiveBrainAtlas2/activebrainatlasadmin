from django.contrib.auth.models import User
import datetime
from neuroglancer.models import Structure, LayerData
from brain.models import Animal
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.atlas import get_scales
from timeit import default_timer as timer

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
MANUAL = 1
CORRECTED = 2
POINT_ID = 52


def update_annotation_data_old_method(urlModel):
    """
    This method checks if there is center of mass data. If there is,
    then it first find the center of mass rows for that
    person/input_type/animal/active combination.
    If data already exists for that combination above, it all gets set to
    inactive. Then the new data gets inserted. No updates!
    It does lots of checks to make sure it is in the correct format,
    including:
        layer must be named COM
        structure name must be in the description field
        structures must exactly match the structure names in the database,
        though this script does strip line breaks, white space off.
    :param urlModel: the long url from neuroglancer
    :return: nothing
    """
    json_txt = urlModel.url
    try:
        loggedInUser = User.objects.get(pk=urlModel.person.id)
    except User.DoesNotExist:
        logger.error("User does not exist")
        return
    try:
        prep = Animal.objects.get(pk=urlModel.animal)
    except Animal.DoesNotExist:
        logger.error("Animal does not exist")
        return
    if 'layers' in json_txt:
        layers = json_txt['layers']
        for layer in layers:
            if 'annotations' in layer:
                layer_name = str(layer['name']).strip()
                if layer_name != 'annotation':
                    print('layer=', layer_name)
                    existing_structures = get_existing_structures(prep, loggedInUser, layer_name)
                    remaining_structures = update_or_insert_annotations(prep, layer, loggedInUser, existing_structures, layer_name)
                    for structure in remaining_structures:
                        delete_annotation(prep, structure, loggedInUser, layer_name)

def update_or_insert_annotations(prep, layer, loggedInUser, existing_structures, layer_name):
    scale_xy, z_scale = get_scales(prep.prep_id)
    annotations = layer['annotations']
    for annotation in annotations:
        x = annotation['point'][0] * scale_xy
        y = annotation['point'][1] * scale_xy
        z = annotation['point'][2] * z_scale
        if 'description' in annotation:
            structure = get_structure(annotation)
            if structure is not None and prep is not None and loggedInUser is not None:
                if structure.id in existing_structures:
                    update_annotation(prep, (x, y, z), structure, loggedInUser, layer_name)
                    existing_structures.discard(structure.id)
                else:
                    add_annotation(prep, structure, (x, y, z), loggedInUser, layer_name)
    return existing_structures


def add_annotation(prep, structure, coordinates, loggedInUser, layer):
    print(f'adding {structure}')
    x, y, z = coordinates
    try:
        LayerData.objects.create(
            prep=prep, structure=structure, created=datetime.datetime.now(),
            layer=layer, active=True, person=loggedInUser, input_type_id=MANUAL,
            x=x, y=y, section=z)
    except Exception as e:
        logger.error(f'Error inserting manual {structure.abbreviation}', e)


def update_annotation(prep, coordinates, structure, loggedInUser, layer):
    x, y, z = coordinates
    LayerData.objects.filter(input_type_id=MANUAL)\
        .filter(prep=prep)\
        .filter(active=True)\
        .filter(layer=layer)\
        .filter(structure=structure)\
        .update(x=x, y=y, section=z,
                updatedby=loggedInUser,
                updated=datetime.datetime.now())    


def delete_annotation(prep, structure, loggedInUser, layer):
    LayerData.objects.filter(person=loggedInUser)\
    .filter(input_type_id=MANUAL)\
    .filter(prep=prep)\
    .filter(active=True)\
    .filter(layer=layer)\
    .filter(structure_id=structure)\
    .delete()


def get_existing_structures(prep, loggedInUser, layer):
    existing_structures = set()
    existing_layer_data = LayerData.objects.filter(input_type_id=MANUAL)\
        .filter(prep=prep)\
        .filter(active=True)\
        .filter(person=loggedInUser)\
        .filter(layer=layer)\

    for s in existing_layer_data:
        existing_structures.add(s.structure.id)
    return existing_structures


def update_annotation_data(neuroglancerModel):
    """
    This is the method from brainsharer_portal
    """
    start = timer()
    json_txt = neuroglancerModel.url
    try:
        loggedInUser = User.objects.get(pk=neuroglancerModel.person.id)
    except User.DoesNotExist:
        logger.error("User does not exist")
        return
    try:
        prep = Animal.objects.get(pk=neuroglancerModel.animal)
    except Animal.DoesNotExist:
        logger.error("Animal does not exist")
        return
    if 'layers' in json_txt:
        layers = json_txt['layers']
        for layer in layers:
            if 'annotations' in layer:
                layer_name = str(layer['name']).strip()
                if prep is not None and loggedInUser is not None and \
                    layer_name != 'annotation':
                    inactivate_annotations(prep, loggedInUser, layer_name)
                    bulk_annotations(prep, layer, loggedInUser, layer_name)
                
    end = timer()
    print(f'Updating all annotations took {end - start} seconds')


def inactivate_annotations(prep, loggedInUser, layer_name):
    """
    Update the existing annotations that are manual, prep, active 
    set them to inactive
    """
    LayerData.objects.filter(input_type_id=MANUAL)\
    .filter(prep=prep)\
    .filter(active=True)\
    .filter(layer=layer_name)\
    .update(active=False, updatedby=loggedInUser)


def bulk_annotations(prep, layer, loggedInUser, layer_name):
    start = timer()
    bulk_mgr = BulkCreateManager(chunk_size=200)
    scale_xy, z_scale = get_scales(prep.prep_id)
    annotations = layer['annotations']
    for annotation in annotations:
        x1 = annotation['point'][0] * scale_xy
        y1 = annotation['point'][1] * scale_xy
        z1 = annotation['point'][2] * z_scale
        structure = get_structure(annotation)
        if structure is not None:
            bulk_mgr.add(LayerData(prep=prep, structure=structure, created=datetime.datetime.now(),
            layer=layer_name, active=True, person=loggedInUser, input_type_id=MANUAL,
            x=x1, y=y1, section=z1))
    bulk_mgr.done()
    end = timer()
    print(f'Inserting {layer_name} annotations took {end - start} seconds')


def get_structure(annotation):
    structure = Structure.objects.get(pk=POINT_ID)
    if 'description' in annotation:
        abbreviation = str(annotation['description']).replace('\n', '').strip()
        try:
            structure = Structure.objects.get(abbreviation=abbreviation)
        except Structure.DoesNotExist:
            logger.error(f'Structure {abbreviation} does not exist')
    return structure
