"""
Background tasks must be in a file named: tasks.py
Don't move it to another file!
"""
from django.http import Http404
from background_task import background
from neuroglancer.bulk_insert import BulkCreateManager
from neuroglancer.models import AnnotationPointArchive, AnnotationSession

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