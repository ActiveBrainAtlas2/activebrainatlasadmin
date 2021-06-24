from timeit import default_timer as timer
from neuroglancer.atlas import get_centers_dict
import numpy as np
import pandas as pd

def get_common_structure(brains):
    start = timer()
    common_structures = set()
    for brain in brains:
        common_structures = common_structures | set(get_centers_dict(brain).keys())
    common_structures = list(sorted(common_structures))
    end = timer()
    print(f'get common structures took {end - start} seconds')
    return common_structures


def get_brain_coms(brains, person_id, input_type_id):
    start = timer()
    brain_coms = {}
    for brain in brains:
        brain_coms[brain] = get_centers_dict(prep_id=brain, 
        person_id=person_id, 
        input_type_id=input_type_id)
    end = timer()
    print(f'get brain coms took {end - start} seconds to fetch {len(brain_coms)} centers')
    return brain_coms

def prepare_table_for_plot(atlas_coms, common_structures, brains, person_id, input_type_id):
    start = timer()
    brain_coms = get_brain_coms(brains, input_type_id = input_type_id, person_id = person_id )
    df = pd.DataFrame()
    for brain in brain_coms.keys():
        offset = [brain_coms[brain][s] - atlas_coms[s]
                  if s in brain_coms[brain] else [np.nan, np.nan, np.nan]
                  for s in common_structures]
        offset = np.array(offset)
        scale = np.array([10, 10, 20])
        dx, dy, dz = (offset * scale).T
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
    end = timer()
    print(f'prepare table for plot took {end - start} seconds')
    return df

def add_trace(df,fig,rowi):
    start = timer()
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
    end = timer()
    print(f'add_trace took {end - start} seconds')


