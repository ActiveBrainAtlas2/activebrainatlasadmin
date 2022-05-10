from django.urls import path, include
from neuroglancer import views
from rest_framework import routers
app_name = 'neuroglancer'

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', views.UrlViewSet, basename='neuroglancer')

transformation_relate_urls = [
    path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<int:reverse>', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<str:reference_scales>', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<int:reverse>/<str:reference_scales>', views.Rotation.as_view()),
    path('rotations', views.GetComList.as_view()),
]
volume_related_urls = [
    path('get_volume/<str:prep_id>/<str:label>/<int:input_type_id>', views.GetVolume.as_view()),
    path('get_volume_list', views.GetComList.as_view()),
    path('contour_to_segmentation/<int:url_id>/<str:volume_id>',views.ContoursToVolume.as_view(),name = 'contour_to_segmentation'),
]
general_urls = [
    path('', include(router.urls)),
    path(r'public', views.public_list, name='public'),
    path('landmark_list',views.LandmarkList.as_view()),
    path('annotation_status',views.AnnotationStatus.as_view(),name = 'status'),
    path('save_annotations/<int:url_id>/<str:annotation_layer_name>',views.SaveAnnotation.as_view(),name = 'save_annotations'),]

com_related_urls = [
    path('get_com/<str:prep_id>/<str:label>/<int:input_type_id>', views.GetCOM.as_view()),
    path('get_com_list', views.GetComList.as_view()),
]
marked_cell_related_urls = [
    path('get_marked_celll/<str:prep_id>/<str:label>/<int:input_type_id>', views.GetMarkedCell.as_view()),
    path('get_marked_cell_list', views.GetComList.as_view()),
    path('cell_types',views.GetCellTypes.as_view(),name = 'cell_types'),
]

urlpatterns = general_urls+transformation_relate_urls+volume_related_urls+com_related_urls+marked_cell_related_urls