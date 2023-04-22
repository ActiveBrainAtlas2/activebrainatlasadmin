"""
Background tasks must be in a file named: tasks.py
Don't move it to another file!
They also cannot accept objects as arguments. 
**Note: If you modify the tasks.py file, you must restart supervisord on the web server!!!**
``sudo systemctl restart supervisord.service``
"""
from neuroglancer.models import NeuroglancerState
from neuroglancer.annotation_manager import AnnotationManager, DEBUG
from timeit import default_timer as timer

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
    start_time = timer()
    manager.set_current_layer(layeri) # This takes a LONG time for polygons/volumes!
    if DEBUG:
        end_time = timer()
        total_elapsed_time = round((end_time - start_time),2)
        print(f'Setting current layer took {total_elapsed_time} seconds.')

    assert manager.animal is not None
    assert manager.annotator is not None

    start_time = timer()
    manager.insert_annotations()
    if DEBUG:
        end_time = timer()
        total_elapsed_time = round((end_time - start_time),2)
        print(f'Inserting all annotations took {total_elapsed_time} seconds.')

