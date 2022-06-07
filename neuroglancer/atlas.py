"""
Some important static methods used throughout the Django project.
"""
import numpy as np
from neuroglancer.models import BrainRegion, LAUREN_ID, \
            PolygonSequence, MarkedCell, StructureCom
from brain.models import Animal, ScanRun
from abakit.registration.algorithm import umeyama
import logging
from neuroglancer.AnnotationBase import AnnotationBase
logging.basicConfig()
logger = logging.getLogger(__name__)
MANUAL = 1
CORRECTED = 2

def align_atlas(animal,annotator_id,source,reverse = False,reference_scales = None):
    """
    This prepares the data for the align_point_sets method.
    Make sure we have at least 3 points
    :param animal: the animal we are aligning to
    :param input_type_id: the int defining what type of input. Taken from the
    input_type table with  column=id
    :param owner_id: the int defining the person. Taken from the auth_user
    table column=id
    :return: a 3x3 matrix and a 1x3 matrix
    """
    atlas_centers = get_annotation_dict('atlas',16,'MANUAL')
    reference_centers = get_annotation_dict(animal,annotator_id,source)
    try:
        scanRun = ScanRun.objects.get(prep__prep_id=animal)
    except ScanRun.DoesNotExist:
        scanRun = None
    if len(reference_centers) > 2 and scanRun is not None:
        if reference_scales is None:
            resolution = scanRun.resolution
            reference_scales = (resolution, resolution, scanRun.zresolution)
        brain_regions = sorted(reference_centers.keys())
        common_keys = atlas_centers.keys() & reference_centers.keys()
        dst_point_set = np.array([atlas_centers[s] for s in brain_regions if s in common_keys]).T
        src_point_set = np.array([reference_centers[s] for s in brain_regions if s in common_keys]).T
        if reverse:
            copy = dst_point_set
            dst_point_set = src_point_set
            src_point_set = copy
        R, t = umeyama(src_point_set, dst_point_set)
        t = t / np.array([reference_scales]).T # production version
    else:
        R = np.eye(3)
        t = np.zeros((3,1))
    return R, t

def get_annotation_dict(prep_id, annotator_id,source):
    '''
    This method replaces get_centers_dict and get_layer_data_row
    :param prep_id: string name of animal
    :param label: formerly layer, the string name of the layer
    '''


    row_dict = {}
    try:
        animal = Animal.objects.get(pk=prep_id)
    except Animal.DoesNotExist:
        logger.error(f'Error, {prep_id} does not exist in DB. Method: get_annotation_dict is returning an empty dictionary.')
        return row_dict
    base = AnnotationBase()
    base.set_animal_from_id(prep_id)
    base.set_annotator_from_id(annotator_id)
    rows = StructureCom.objects.filter(annotation_session__animal=base.animal)\
                .filter(source=source).filter(annotation_session__annotator=base.annotator)
    brain_region_dict = {}
    brain_regions = BrainRegion.objects.filter(active=True).all()
    for brain_region in brain_regions:
        brain_region_dict[brain_region.id] = brain_region.abbreviation
    for row in rows:
        brain_region_id = row.annotation_session.brain_region.id
        abbreviation = brain_region_dict[brain_region_id]
        row_dict[abbreviation] = [row.x, row.y, row.z]
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
