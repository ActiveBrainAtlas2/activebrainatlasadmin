"""
These are methods taken from notebooks, mostly Bili's
There are constants defined in the models.py script and imported here
so we can resuse them througout the code.
"""
import numpy as np
from django.contrib.auth.models import User

from neuroglancer.models import Structure, LayerData, Transformation, \
    LAUREN_ID, ATLAS_Z_BOX_SCALE
from brain.models import Animal, ScanRun
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
MANUAL = 1


def align_point_sets(src, dst, with_scaling=True):
    """
    Analytically computes a transformation that minimizes the squared error between source and destination.
    ------------------------------------------------------
    src is the dictionary of the brain we want to align
    dst is the dictionary of the atlas structures
    Defaults to scaling true, which means the transformation is rigid and a uniform scale.
    returns the linear transformation r, and the translation vector t
    """
    assert src.shape == dst.shape
    assert len(src.shape) == 2
    m, n = src.shape  # dimension, number of points

    src_mean = np.mean(src, axis=1).reshape(-1, 1)
    dst_mean = np.mean(dst, axis=1).reshape(-1, 1)

    src_demean = src - src_mean
    dst_demean = dst - dst_mean

    u, s, vh = np.linalg.svd(dst_demean @ src_demean.T / n)

    # deal with reflection
    e = np.ones(m)
    if np.linalg.det(u) * np.linalg.det(vh) < 0:
        print('reflection detected')
        e[-1] = -1

    r = u @ np.diag(e) @ vh

    if with_scaling:
        src_var = (src_demean ** 2).sum(axis=0).mean()
        c = sum(s * e) / src_var
        r *= c

    t = dst_mean - r @ src_mean
    return r, t

def align_atlas(animal, input_type_id=None, person_id=None):
    """
    This prepares the data for the align_point_sets method.
    Make sure we have at least 3 points
    :param animal: the animal we are aligning to
    :param input_type_id: the int defining what type of input. Taken from the com_type table with 
    column=id
    :param person_id: the int defining the person. Taken from the auth_user table column=id
    :return: a 3x3 matrix and a 1x3 matrix
    """

    atlas_centers = get_centers_dict('atlas', input_type_id=MANUAL, person_id=LAUREN_ID)
    reference_centers = get_centers_dict(animal, input_type_id=input_type_id, person_id=person_id)
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

        R, t = align_point_sets(src_point_set, dst_point_set)
        t = t / np.array([reference_scales]).T # production version
<<<<<<< HEAD
        #t = t / np.array([atlas_box_scales]).T # this is NOT in production

    else:
        R = np.eye(3)
        t = np.zeros(3)
        t = t.reshape(3,1)
=======

    else:
        R = np.eye(3)
        t = np.zeros((3,1))
>>>>>>> 2506b46b783fcb79b7a2a01c72870d13be9b69fb
    return R, t

def brain_to_atlas_transform(
    brain_coord, r, t,
    brain_scale=(0.325, 0.325, 20),
    atlas_scale=(10, 10, 20)):
    """
    Takes an x,y,z brain coordinates as a list, and a rotation matrix and transform vector.
    Returns the point in atlas coordinates.
    
    The provided r, t is the affine transformation from brain to atlas such that:
        t_phys = atlas_scale @ t
        atlas_coord_phys = r @ brain_coord_phys + t_phys

    The corresponding reverse transformation is:
        brain_coord_phys = r_inv @ atlas_coord_phys - r_inv @ t_phys
    """
    brain_scale = np.diag(brain_scale)
    atlas_scale = np.diag(atlas_scale)

    # Bring brain coordinates to physical space
    brain_coord = np.array(brain_coord).reshape(3, 1) # Convert to a column vector
    brain_coord_phys = brain_scale @ brain_coord
    
    # Apply affine transformation in physical space
    # The next line corresponds to method: align_atlas atlas_scales
    t_phys = brain_scale @ t
    atlas_coord_phys = r @ brain_coord_phys + t_phys

    # Bring atlas coordinates back to atlas space
    atlas_coord = np.linalg.inv(atlas_scale) @ atlas_coord_phys

    return atlas_coord.T[0] # Convert back to a row vector

def atlas_to_brain_transform(
    atlas_coord, r, t,
    brain_scale=(0.325, 0.325, 20),
    atlas_scale=(10, 10, 20)):
    """
    Takes an x,y,z atlas coordinates, and a rotation matrix and transform vector.
    Returns the point in brain coordinates.
    
    The provided r, t is the affine transformation from brain to atlas such that:
        t_phys = atlas_scale @ t
        atlas_coord_phys = r @ brain_coord_phys + t_phys

    The corresponding reverse transformation is:
        brain_coord_phys = r_inv @ atlas_coord_phys - r_inv @ t_phys
    """
    brain_scale = np.diag(brain_scale)
    atlas_scale = np.diag(atlas_scale)

    # Bring atlas coordinates to physical space
    atlas_coord = np.array(atlas_coord).reshape(3, 1) # Convert to a column vector
    atlas_coord_phys = atlas_scale @ atlas_coord
    
    # Apply affine transformation in physical space
    t_phys = atlas_scale @ t
    r_inv = np.linalg.inv(r)
    brain_coord_phys = r_inv @ atlas_coord_phys - r_inv @ t_phys

    # Bring brain coordinates back to brain space
    brain_coord = np.linalg.inv(brain_scale) @ brain_coord_phys

    return brain_coord.T[0] # Convert back to a row vector

def get_atlas_centersDEPRECATED(
        atlas_box_size=(1000, 1000, 300),
        atlas_box_scales=(10, 10, 20),
        atlas_raw_scale=10):
    """ atlas_raw_scale=10 refers to 10.0um which means each voxel size is 10 microns
        We want the original COMs entered by the anatomist, in this case it is Lauren
        whose ID = 16
        NOTE, this method has become deprecated as of 29 Jun 2021
    """

        
    atlas_box_scales = np.array(atlas_box_scales)
    atlas_box_size = np.array(atlas_box_size)
    atlas_box_center = atlas_box_size / 2
    atlas_centers = get_centers_dict('atlas', input_type_id=MANUAL, person_id=LAUREN_ID)

<<<<<<< HEAD
    for structure, origin in atlas_centers.items():
        # transform into the atlas box coordinates that neuroglancer assumes
        center = atlas_box_center + np.array(origin) * atlas_raw_scale / atlas_box_scales
=======
    for structure, com in atlas_centers.items():
        # transform into the atlas box coordinates that neuroglancer assumes
        center = atlas_box_center + np.array(com) * atlas_raw_scale / atlas_box_scales
>>>>>>> 2506b46b783fcb79b7a2a01c72870d13be9b69fb
        atlas_centers[structure] = center

    return atlas_centers

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


def update_center_of_mass(urlModel):
    """
    This method checks if there is center of mass data. If there is,
    then it first find the center of mass rows for that person/input_type/animal/active combination.
    If data already exists for that combination above, it all gets set to inactive.
    Then the new data gets inserted. No updates!
    It does lots of checks to make sure it is in the correct format,
    including:
        layer must be named COM
        structure name just be in the description field
        structures must exactly match the structure names in the database,
        though this script does strip line breaks, white space off.
    :param urlModel: the long url from neuroglancer
    :return: nothing
    """
    json_txt = urlModel.url

    try:
        person = User.objects.get(pk=urlModel.person.id)
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
                lname = str(layer['name']).upper().strip()
                if lname == 'COM':
                    LayerData.objects.filter(person=person)\
                        .filter(input_type_id=MANUAL)\
                        .filter(prep=prep)\
                        .filter(active=True)\
                        .filter(layer='COM')\
                        .update(active=False)
                    
                    transformations = Transformation.objects.filter(person=person)\
                        .filter(input_type_id=MANUAL)\
                        .filter(prep=prep)\
                        .filter(active=True).all()

                    if len(transformations) > 0:
                        transformation = transformations[0]
                    else:
                        transformation = None
                    
                    annotation = layer['annotations']
                    for com in annotation:
                        x = com['point'][0]
                        y = com['point'][1]
                        z = com['point'][2]
                        if 'description' in com:
                            abbreviation = str(com['description']).replace(
                                '\n', '').strip()
                            try:
                                structure = Structure.objects.get(
                                    abbreviation=abbreviation)
                            except Structure.DoesNotExist:
                                print(f'Structure {abbreviation} does not exist')
                                logger.error("Structure does not exist")

                            # Create the manual COM
                            if structure is not None and prep is not None and person is not None:
                                try:
                                    LayerData.objects.create(
                                        prep=prep, structure=structure,
                                        transformation = transformation,
                                        layer = 'COM',
                                        active=True, person=person, input_type_id=MANUAL,
                                            x=x, y=y, section=int(z))
                                except:
                                    print(f'Error inserting manual {structure.abbreviation}')
                                    logger.error(f'Error inserting manual {structure.abbreviation}')



def get_common_structures(brains):
    common_structures = set()
    for brain in brains:
        common_structures = common_structures | set(get_centers_dict(brain).keys())
    common_structures = list(sorted(common_structures))
    return common_structures


def get_brain_coms(brains, person_id, input_type_id):
    brain_coms = {}
    for brain in brains:
        brain_coms[brain] = get_centers_dict(prep_id=brain, 
                                            person_id=person_id, 
                                            input_type_id=input_type_id
                                            )
    return brain_coms
