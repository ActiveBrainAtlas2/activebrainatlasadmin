from django.urls import path, include
from neuroglancer import views
from neuroglancer.create_state_views import fetch_layers

from rest_framework import routers
app_name = 'neuroglancer'

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', views.NeuroglancerViewSet, basename='neuroglancer') # private portal data
router.register(r'neuroglancers', views.NeuroglancerPublicViewSet, basename='neuroglancers') # public data
router.register(r'states', views.NeuroglancerAvailableData, basename='states')

general_urls = [
    path('', include(router.urls)),
    path('landmark_list',views.LandmarkList.as_view()),
    path('save_annotations/<int:neuroglancer_state_id>/<str:annotation_layer_name>',views.SaveAnnotation.as_view(),name = 'save_annotations'),
    path('groups', views.NeuroglancerGroupAvailableData.as_view()),
    path('landmark_list',views.LandmarkList.as_view()),
    path('createstate', views.create_state),
    path('fetch_layers/<int:animal_id>', fetch_layers, name='fetch_layers')
]

transformation_relate_urls = [ 
    path('rotation/<str:prep_id>/<int:annotator_id>/<str:source>/', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<int:annotator_id>/<str:source>/<int:reverse>', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<int:annotator_id>/<str:source>/<str:reference_scales>', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<int:annotator_id>/<str:source>/<int:reverse>/<str:reference_scales>', views.Rotation.as_view()),
    path('rotations', views.GetComList.as_view()),
]
volume_related_urls = [
    path('get_volume/<str:session_id>', views.GetVolume.as_view()),
    path('get_volume_list', views.GetPolygonList.as_view()),
    path('contour_to_segmentation/<int:neuroglancer_state_id>/<str:volume_id>',views.ContoursToVolume.as_view(),name = 'contour_to_segmentation'),
]

com_related_urls = [
    path('get_com/<str:prep_id>/<str:annotator_id>/<str:source>', views.GetCOM.as_view()),
    path('get_com_list', views.GetComList.as_view()),
]
marked_cell_related_urls = [
    path('annotations', views.GetMarkedCellList.as_view()),
    path('get_marked_cell_list', views.GetMarkedCellList.as_view()),
    path('get_marked_cell/<str:session_id>', views.GetMarkedCell.as_view()),
    path('cell_types',views.GetCellTypes.as_view(),name = 'cell_types'),
]

urlpatterns = general_urls + transformation_relate_urls + volume_related_urls + \
    com_related_urls + marked_cell_related_urls