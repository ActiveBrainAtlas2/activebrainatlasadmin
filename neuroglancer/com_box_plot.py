import numpy as np
import pandas as pd
import plotly.graph_objects as go
from neuroglancer.atlas import get_centers_dict
from abakit.registration.algorithm import brain_to_atlas_transform, umeyama


def get_common_structure(brains):
    common_structures = set()
    for brain in brains:
        common_structures = common_structures | set(get_centers_dict(brain).keys())
    common_structures = list(sorted(common_structures))
    return common_structures


def prepare_table_for_plot(atlas_coms, common_structures, brains, person_id, input_type_id):
    """
    Notes, 30 Jun 2021
    This works and mimics Bili's notebook on the corrected data, which is what we want
    It uses data from the DB that is all in microns. Make sure you use
    brain coms from person=2 and input type=corrected (id=2)
    """
    df = pd.DataFrame()
    for brain in brains:
        brain_com = get_centers_dict(prep_id=brain,  person_id=2,input_type_id=2)
        if len(brain_com) == 0:
            print('defaulting back to default for ', brain)
            brain_com = get_centers_dict(prep_id=brain,  person_id=person_id,input_type_id=1)

        structures = sorted(brain_com.keys())
        dst_point_set = np.array([atlas_coms[s] for s in structures if s in common_structures]).T
        src_point_set = np.array([brain_com[s] for s in structures if s in common_structures]).T
        r, t = umeyama(src_point_set, dst_point_set)

        offsets = []
        for s in common_structures:
            x = np.nan
            y = np.nan
            section = np.nan
            brain_coords = np.array([x,y,section])
            if s in brain_com:
                brain_coords = np.asarray(brain_com[s])
                transformed = brain_to_atlas_transform(brain_coords, r, t)
            else:
                transformed = np.array([x,y,section])
            offsets.append( transformed - atlas_coms[s] )

        offset = np.array(offsets)
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


