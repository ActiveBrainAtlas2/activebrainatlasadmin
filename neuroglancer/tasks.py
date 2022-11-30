"""
Background tasks must be in a file named: tasks.py
Don't move it to another file!
They also cannot accept objects as arguments. 
"""
import numpy as np
from django.http import Http404
from background_task import background
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.models import AnnotationPointArchive, AnnotationSession, CellType, UrlModel, \
    get_region_from_abbreviation, UNMARKED
from neuroglancer.annotation_manager import AnnotationManager


#@background(schedule=0)
def restore_annotations(archive):
    """Restore a set of annotations associated with an archive.
    1. Get requested archive (set of points in the annotations_points_archive table)
    3. Add it to either marked_cell, polygon_sequence or structureCOM
    4. Deleted that archived data
    5. Update that session to be active

    """

    try:
        annotation_session = archive.annotation_session
    except AnnotationSession.DoesNotExist:
        print('No annotation_session to fetch')
        raise Http404
    data_model = annotation_session.get_session_model()
    field_names = [f.name for f in data_model._meta.get_fields() if not f.name == 'id']
    rows = AnnotationPointArchive.objects.filter(archive=archive)
    batch = []
    for row in rows:
        fields = [getattr(row, field_name) for field_name in field_names]
        input = dict(zip(field_names, fields))
        batch.append(data_model(**input))
    data_model.objects.bulk_create(batch, 50, update_conflicts=True)
    


#@background(schedule=0)
def background_archive_and_insert_annotations(layeri, url_id):
    """The main function that updates the database with annotations in the current_layer attribute
        This function loops each annotation in the curent layer and inserts/archive points in the 
        appropriate table
    """
    urlModel = UrlModel.objects.get(pk=url_id)
    manager = AnnotationManager(urlModel)
    manager.set_current_layer(layeri)

    assert manager.animal is not None
    assert manager.annotator is not None

    manager.archive_and_insert_annotations()
