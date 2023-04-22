from django.urls import path, include
from neuroglancer.views import NeuroglancerViewSet, NeuroglancerPublicViewSet, NeuroglancerAvailableData, LandmarkList, \
    SaveAnnotation, NeuroglancerGroupAvailableData, create_state, Rotation, GetComList, GetVolume, GetPolygonList, ContoursToVolume, \
    GetCOM, GetMarkedCellList, GetMarkedCell, GetCellTypes
from neuroglancer.create_state_views import fetch_layers

from rest_framework import routers
app_name = 'neuroglancer'

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', NeuroglancerViewSet, basename='neuroglancer') # private portal data
router.register(r'neuroglancers', NeuroglancerPublicViewSet, basename='neuroglancers') # public data
router.register(r'states', NeuroglancerAvailableData, basename='states')

general_urls = [
    path('', include(router.urls)),
    path('landmark_list',LandmarkList.as_view()),
    path('save_annotations/<int:neuroglancer_state_id>/<str:annotation_layer_name>',SaveAnnotation.as_view(),name = 'save_annotations'),
    path('groups', NeuroglancerGroupAvailableData.as_view()),
    path('landmark_list',LandmarkList.as_view()),
    path('createstate', create_state),
    path('fetch_layers/<int:animal_id>', fetch_layers, name='fetch_layers')
]

transformation_relate_urls = [ 
    path('rotation/<str:prep_id>/<int:annotator_id>/<str:source>/', Rotation.as_view()),
    path('rotation/<str:prep_id>/<int:annotator_id>/<str:source>/<int:reverse>', Rotation.as_view()),
    path('rotation/<str:prep_id>/<int:annotator_id>/<str:source>/<str:reference_scales>', Rotation.as_view()),
    path('rotation/<str:prep_id>/<int:annotator_id>/<str:source>/<int:reverse>/<str:reference_scales>', Rotation.as_view()),
    path('rotations', GetComList.as_view()),
]
volume_related_urls = [
    path('get_volume/<str:session_id>', GetVolume.as_view()),
    path('get_volume_list', GetPolygonList.as_view()),
    path('contour_to_segmentation/<int:neuroglancer_state_id>/<str:volume_id>',ContoursToVolume.as_view(),name = 'contour_to_segmentation'),
]

com_related_urls = [
    path('get_com/<str:prep_id>/<str:annotator_id>/<str:source>', GetCOM.as_view()),
    path('get_com_list', GetComList.as_view()),
]
marked_cell_related_urls = [
    path('annotations', GetMarkedCellList.as_view()),
    path('get_marked_cell_list', GetMarkedCellList.as_view()),
    path('get_marked_cell/<str:session_id>', GetMarkedCell.as_view()),
    path('cell_types',GetCellTypes.as_view(),name = 'cell_types'),
]

urlpatterns = general_urls + transformation_relate_urls + volume_related_urls + \
    com_related_urls + marked_cell_related_urls