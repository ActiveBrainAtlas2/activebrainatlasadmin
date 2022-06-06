"""
Background tasks must be in a file named: tasks.py
Don't move it to another file!
"""
from django.http import Http404
import numpy as np
from background_task import background
from neuroglancer.bulk_insert import BulkCreateManager

from neuroglancer.models import AnnotationPointArchive, AnnotationSession, get_region_from_abbreviation


# @background(schedule=0)
def archive_and_insert_annotations():
    """#TODO fix this method so it is a standalone method and not part of a class
    The main function that updates the database with annotations in the current_layer attribute
    This function loops each annotation in the curent layer and inserts/archive points in the 
    appropriate table
    marked_cells = []
    bulk_mgr = BulkCreateManager(chunk_size=100)

    for annotationi in current_layer.annotations:
        if annotationi.is_com():
            brain_region = get_region_from_abbreviation(annotationi.get_description())
            new_session = get_new_session_and_archive_points(brain_region=brain_region,annotation_type='STRUCTURE_COM')
            add_com(annotationi,new_session)
        if annotationi.is_cell():
            marked_cells.append(annotationi)
        if annotationi.is_polygon():
            brain_region = get_region_from_abbreviation('polygon')
            new_session = get_new_session_and_archive_points(brain_region=brain_region,annotation_type='POLYGON_SEQUENCE')
            add_polygons(annotationi,new_session)
        if annotationi.is_volume():
            brain_region = get_region_from_abbreviation(annotationi.get_description())
            new_session = get_new_session_and_archive_points(brain_region=brain_region,annotation_type='POLYGON_SEQUENCE')
            add_volumes(annotationi,new_session)
    if len(marked_cells)>0:
        categories = np.array([i.category for i in marked_cells])
        unique_category = np.unique(categories)
        for category in unique_category:
            in_category = categories == category
            cells = marked_cells[in_category]
            new_session = get_new_session_and_archive_points(brain_region=brain_region,annotation_type='MARKED_CELL')
            for annotationi in cells:
                cell_type = CellType.objects.filter(cell_type = category).first()
                if cell_type is not None:
                    brain_region = get_region_from_abbreviation('point')
                    add_marked_cells(annotationi,new_session,cell_type)
    bulk_mgr.done()
    """
    pass


@background(schedule=0)
def restore_annotations(session_id):
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
        annotation_session = AnnotationSession.objects.get(pk=session_id)
    except AnnotationSession.DoesNotExist:
        print('No annotation_session to fetch')
        raise Http404
    data_model = annotation_session.get_session_model()
    data_model.objects.filter(annotation_session=annotation_session).delete()
    field_names = [f.name for f in data_model._meta.get_fields() if not f.name == 'id']
    rows = AnnotationPointArchive.objects.filter(annotation_session=annotation_session)
    bulk_mgr = BulkCreateManager(chunk_size=100)
    for row in rows:
        fields = [getattr(row,namei) for namei in field_names]
        input = dict(zip(field_names,fields))
        bulk_mgr.add(data_model(**input))
    bulk_mgr.done()