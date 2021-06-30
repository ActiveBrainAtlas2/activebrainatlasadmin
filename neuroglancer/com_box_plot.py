from brain.models import ScanRun
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from neuroglancer.models import LayerData, Structure


def get_common_structure(brains):
    common_structures = set()
    for brain in brains:
        common_structures = common_structures | set(get_centers_dict(brain).keys())
    common_structures = list(sorted(common_structures))
    return common_structures


def get_brain_coms(brains, person_id, input_type_id):
    brain_coms = {}
    for brain in brains:
        brain_dict = get_centers_dict(prep_id=brain,  person_id=person_id,input_type_id=input_type_id)
        if len(brain_dict) == 0:
            brain_dict = get_centers_dict(prep_id=brain,  person_id=person_id,input_type_id=1)

        brain_coms[brain] = brain_dict
    return brain_coms

def prepare_table_for_plot(atlas_coms, common_structures, brains, person_id, input_type_id):
    df = pd.DataFrame()
    for brain in brains:
        ##WORKSbrain_com = get_centers_dict(prep_id=brain,  person_id=28,input_type_id=4)
        brain_com = get_centers_dict(prep_id=brain,  person_id=2,input_type_id=2)
        if len(brain_com) == 0:
            print('defaulting back to default for ', brain)
            brain_com = get_centers_dict(prep_id=brain,  person_id=person_id,input_type_id=1)
        
        try:
            scan_run = ScanRun.objects.filter(prep_id=brain)[0]
        except ScanRun.DoesNotExist:
            print('no scan run for ', brain)

        structures = sorted(brain_com.keys())
        common_keys = atlas_coms.keys() & brain_com.keys()
        dst_point_set = np.array([atlas_coms[s] for s in structures if s in common_keys]).T
        src_point_set = np.array([brain_com[s] for s in structures if s in common_keys]).T

        r, t = align_point_sets(src_point_set, dst_point_set)
        #brain_scale = [scan_run.resolution, scan_run.resolution, 20]
        #brain_scale = [1,1,1]
        #t = t / np.array(brain_scale) # production version
        #t = t.T
        #r, t = align_atlas(brain, input_type_id=1, person_id=2)
        #r, t = get_transformation_matrix(brain)

        scale = np.array([10, 10, 20])
         
        #print(brain, t)

        offsets = []
        for s in common_structures:
            x = np.nan
            y = np.nan
            section = np.nan
            brain_coords = np.array([x,y,section])
            if s in brain_com:
                brain_coords = np.asarray(brain_com[s])
                #brain_coords = r @ brain_coords + t
                #transformed =  brain_coords.T[0] # Convert back to a row vector
                # mimic add aligned
                transformed = brain_to_atlas_transform(brain_coords, r, t)

                #transformed = brain_coords
            else:
                transformed = np.array([x,y,section])
            #transformed = transformed / scale
            # transforms have to be scaled when they are transformed in the DB with pid=28 and ITID=4
            offsets.append( transformed - atlas_coms[s] )

        #offsetX = [brain_coms[brain][s] - atlas_coms[s]
        #          if s in brain_coms[brain] else [np.nan, np.nan, np.nan]
        #          for s in common_structures]
        offset = np.array(offsets)
        #scale = np.array([10, 10, 20])
        #scale = np.array([1, 1, 1])
        #dx, dy, dz = (offset * scale).T
        dx, dy, dz = (offset).T
        dist = np.sqrt(dx * dx + dy * dy + dz * dz)
        df_brain = pd.DataFrame()
        for data_type in ['dx','dy','dz','dist']:
            data = {}
            data['structure'] = common_structures
            data['value'] = eval(data_type)
            data['type'] = data_type
            df_brain = df_brain.append(pd.DataFrame(data), ignore_index=True)
        df_brain['brain'] = brain
        df = df.append(df_brain, ignore_index=True)
    return df


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

    atlas_box_size=(1000, 1000, 300)
    atlas_box_scales=(10, 10, 20)
    atlas_centers = get_atlas_centers(atlas_box_size, atlas_box_scales, 20)
    reference_centers = get_centers_dict(animal, input_type_id=input_type_id, person_id=person_id)
    try:
        scanRun = ScanRun.objects.get(prep__prep_id=animal)
    except ScanRun.DoesNotExist:
        scanRun = None

    if len(reference_centers) > 2 and scanRun is not None:
        resolution = scanRun.resolution
        reference_scales = (resolution, resolution, 20)
        structures = sorted(reference_centers.keys())
        # align animal to atlas
        common_keys = atlas_centers.keys() & reference_centers.keys()
        dst_point_set = np.array([atlas_centers[s] for s in structures if s in common_keys]).T
        ###PART1dst_point_set = np.diag(atlas_box_scales) @ dst_point_set
        src_point_set = np.array([reference_centers[s] for s in structures if s in common_keys]).T
        src_point_set = np.diag(reference_scales) @ src_point_set

        R, t = align_point_sets(src_point_set, dst_point_set)
        t = t / np.array([reference_scales]).T # production version

    else:
        R = np.eye(3)
        t = np.zeros((3,1))
    return R, t

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


def brain_to_atlas_transform(brain_coord, r, t):
    """
    Takes an x,y,z brain coordinates as a list, and a rotation matrix and transform vector.
    Returns the point in atlas coordinates.
    
    The provided r, t is the affine transformation from brain to atlas such that:
        t_phys = atlas_scale @ t
        atlas_coord_phys = r @ brain_coord_phys + t_phys

    The corresponding reverse transformation is:
        brain_coord_phys = r_inv @ atlas_coord_phys - r_inv @ t_phys
    """
    brain_scale=(1,1,1)
    atlas_scale=(1,1,1)
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

    altas_coord = r @ brain_coord + t

    return atlas_coord.T[0] # Convert back to a row vector


def add_trace(df,fig,rowi):
    colors = ["#ee6352","#08b2e3","#484d6d","#57a773"]
    colori = 0
    for row_type in ['dx','dy','dz','dist']:
        rows_of_type = df[df.type==row_type]
        fig.append_trace(
            go.Scatter(x=rows_of_type['structure'],
                y=rows_of_type['value'],mode='markers', 
                marker_color = colors[colori],
                name = row_type,
                text=rows_of_type['brain']),
                row = rowi,col=1
                )
        colori+=1


