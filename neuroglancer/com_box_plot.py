from brain.models import ScanRun
from neuroglancer.atlas import align_atlas, brain_to_atlas_transform, get_centers_dict
import numpy as np
import pandas as pd
import plotly.graph_objects as go

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
    brain_coms = get_brain_coms(brains, input_type_id = input_type_id, person_id = person_id )
    df = pd.DataFrame()
    for brain in brain_coms.keys():
        
        try:
            scan_run = ScanRun.objects.filter(prep_id=brain)[0]
        except ScanRun.DoesNotExist:
            print('no scan run for ', brain)

        r, t = align_atlas(brain, input_type_id=input_type_id, person_id=person_id)
        if np.sum(t) == 0:
            print('no rotation matrix for', brain)
            r, t = align_atlas(brain, input_type_id=1, person_id=person_id)
        brain_scale = [scan_run.resolution, scan_run.resolution, 20]
        offsets = []
        for s in common_structures:
            x = np.nan
            y = np.nan
            section = np.nan
            brain_coords = np.array([x,y,section])
            if s in brain_coms[brain]:
                brain_coords = np.asarray(brain_coms[brain][s])
                transformed = brain_to_atlas_transform(brain_coords, r, t, brain_scale=brain_scale)
            else:
                transformed = np.array([x,y,section])
            offsets.append( transformed - atlas_coms[s] )

        #offsetX = [brain_coms[brain][s] - atlas_coms[s]
        #          if s in brain_coms[brain] else [np.nan, np.nan, np.nan]
        #          for s in common_structures]
        offset = np.array(offsets)
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


