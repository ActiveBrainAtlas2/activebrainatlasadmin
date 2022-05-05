from django.urls import path, include
from neuroglancer import views
from rest_framework import routers
app_name = 'neuroglancer'

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', views.UrlViewSet, basename='neuroglancer')

urlpatterns = [
    path('', include(router.urls)),
    path(r'public', views.public_list, name='public'),
    path('get_com/<str:prep_id>/<str:label>/<int:input_type_id>', views.GetCOM.as_view()),
    path('get_volume/<str:prep_id>/<str:label>/<int:input_type_id>', views.GetVolume.as_view()),
    path('get_marked_celll/<str:prep_id>/<str:label>/<int:input_type_id>', views.GetMarkedCell.as_view()),
    path('get_com_list', views.GetComList.as_view()),
    path('get_volume_list', views.GetComList.as_view()),
    path('get_marked_cell_list', views.GetComList.as_view()),

    path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<int:reverse>', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<str:reference_scales>', views.Rotation.as_view()),
    path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<int:reverse>/<str:reference_scales>', views.Rotation.as_view()),
    path('rotations', views.GetComList.as_view()),

    path('landmark_list',views.LandmarkList.as_view()),
    path('annotation_status',views.AnnotationStatus.as_view(),name = 'status'),
    path('contour_to_segmentation/<int:url_id>/<str:volume_id>',views.ContoursToVolume.as_view(),name = 'contour_to_segmentation'),
    path('save_annotations/<int:url_id>/<str:annotation_layer_name>',views.SaveAnnotation.as_view(),name = 'save_annotations'),
    path('cell_types',views.GetCellTypes.as_view(),name = 'cell_types'),
]