"""
Background tasks must be in a file named: tasks.py
Don't move it to another file!
They also cannot accept objects as arguments. 
**Note: If you modify the tasks.py file, you must restart supervisord on the web server!!!**
``sudo systemctl restart supervisord.service``
"""
from neuroglancer.models import AnnotationPointArchive, AnnotationSession, NeuroglancerState
from neuroglancer.annotation_manager import AnnotationManager
from authentication.models import User


def restore_annotations(archiveSet):
    """Restore a set of annotations associated with an archive.

    #. Get requested archive (set of points in the annotations_points_archive table)
    #. Mark session inactive that is in the archive
    #. Create a new active session and add it to either marked_cell, polygon_sequence or structureCOM

    :param archive: ArchiveSet object we want to restore
    """

    session = archiveSet.annotation_session
    data_model = session.get_session_model()
    session.active = False
    session.save()
    archiveSet.active = False
    archiveSet.save()
    new_session = AnnotationSession.objects.create(
            animal=session.animal,
            neuroglancer_model=session.neuroglancer_model,
            brain_region=session.brain_region,
            annotator=session.annotator,
            annotation_type=session.annotation_type, 
            active=True)

    field_names = [f.name for f in data_model._meta.get_fields() if not f.name == 'id']
    rows = AnnotationPointArchive.objects.filter(archive=archiveSet)
    batch = []
    for row in rows:
        fields = [getattr(row, field_name) for field_name in field_names]
        input = dict(zip(field_names, fields))
        input['annotation_session'] = new_session
        batch.append(data_model(**input))
    data_model.objects.bulk_create(batch, 50)
    

def background_archive_and_insert_annotations(layeri, neuroglancer_state_id):
    """The main function that updates the database with annotations in the current_layer attribute
        This function loops each annotation in the curent layer and inserts/archive points in the 
        appropriate table. It calls the nobackground method, but since it is annotated
        with the background decorator, it will run in the background.

    :param layeri: the active layer in Neuroglancer we are working on
    :param neuroglancer_state_id: the primary key of the Neuroglancer state
    """
    
    nobackground_archive_and_insert_annotations(layeri, neuroglancer_state_id)

def nobackground_archive_and_insert_annotations(layeri, neuroglancer_state_id):
    """Same as the background_archive_and_insert_annotations method except
    it does not use supervisord and does not go into a background process.
    This will take a while to run for the user.

    :param layeri: the active layer in Neuroglancer we are working on
    :param neuroglancer_state_id: the primary key of the Neuroglancer state
    """

    neuroglancerState = NeuroglancerState.objects.get(pk=neuroglancer_state_id)
    manager = AnnotationManager(neuroglancerState)
    manager.set_current_layer(layeri) # This takes a LONG time for polygons/volumes!

    assert manager.animal is not None
    assert manager.annotator is not None

    manager.insert_annotations()

