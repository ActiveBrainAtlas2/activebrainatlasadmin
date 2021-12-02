"""
These are methods taken from notebooks, mostly Bili's
There are constants defined in the models.py script and imported here
so we can resuse them througout the code.
"""
import numpy as np
from django.contrib.auth.models import User
import datetime
from neuroglancer.models import Structure, LayerData, LAUREN_ID, \
    ATLAS_Z_BOX_SCALE
from brain.models import Animal, ScanRun
from abakit.registration.algorithm import umeyama
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
MANUAL = 1
CORRECTED = 2

monitored_layer_names = {'COM':'COM','ADDITIONAL MANUAL ANNOTATIONS':'COM_addition'}

def align_atlas(animal, input_type_id=None, person_id=None):
    """
    This prepares the data for the align_point_sets method.
    Make sure we have at least 3 points
    :param animal: the animal we are aligning to
    :param input_type_id: the int defining what type of input. Taken from the
    com_type table with  column=id
    :param person_id: the int defining the person. Taken from the auth_user
    table column=id
    :return: a 3x3 matrix and a 1x3 matrix
    """

    atlas_centers = get_centers_dict('atlas',
                                     input_type_id=MANUAL,
                                     person_id=LAUREN_ID)
    reference_centers = get_centers_dict(animal,
                                         input_type_id=input_type_id,
                                         person_id=person_id)
    try:
        scanRun = ScanRun.objects.get(prep__prep_id=animal)
    except ScanRun.DoesNotExist:
        scanRun = None

    if len(reference_centers) > 2 and scanRun is not None:
        resolution = scanRun.resolution
        reference_scales = (resolution, resolution, ATLAS_Z_BOX_SCALE)
        structures = sorted(reference_centers.keys())
        # align animal to atlas
        common_keys = atlas_centers.keys() & reference_centers.keys()
        dst_point_set = np.array([atlas_centers[s] for s in structures if s in common_keys]).T
        src_point_set = np.array([reference_centers[s] for s in structures if s in common_keys]).T
        R, t = umeyama(src_point_set, dst_point_set)
        t = t / np.array([reference_scales]).T # production version

    else:
        R = np.eye(3)
        t = np.zeros((3,1))
    return R, t

def get_centers_dict(prep_id, input_type_id=0, person_id=None):
    rows = LayerData.objects.filter(prep__prep_id=prep_id)\
        .filter(active=True).filter(layer='COM')\
            .order_by('structure', 'updated')
    if input_type_id > 0:
        rows = rows.filter(input_type_id=input_type_id)
    if person_id is not None:
        rows = rows.filter(person_id=person_id)
    structure_dict = {}
    structures = Structure.objects.filter(active=True).all()
    for structure in structures:
        structure_dict[structure.id] = structure.abbreviation
    row_dict = {}
    for row in rows:
        structure_id = row.structure_id
        abbreviation = structure_dict[structure_id]
        # do transform here.
        row_dict[abbreviation] = [row.x, row.y, row.section]
    return row_dict

def get_scales(prep_id):
    """
    A generic method to safely query and return resolutions
    param: prep_id varchar of the primary key of the animal
    """
    try:
        query_set = ScanRun.objects.filter(prep_id=prep_id)
    except ScanRun.DoesNotExist:
        scan_run = None
    if query_set is not None and len(query_set) > 0:
        scan_run = query_set[0]
        scale_xy = scan_run.resolution
        z_scale = scan_run.zresolution
    else:
        scale_xy = 1
        z_scale = 1
    return scale_xy, z_scale
