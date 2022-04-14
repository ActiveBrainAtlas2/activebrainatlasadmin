from django.urls import path, include
from neuroglancer import views
from rest_framework import routers
app_name = 'neuroglancer'

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', views.UrlViewSet, basename='neuroglancer')

urlpatterns = [
    path('', include(router.urls)),
    path(r'public', views.public_list, name='public'),
    path('annotation/<str:obj>/<str:prep_id>/<str:label>', views.Annotation.as_view()),
    path('annotations', views.Annotations.as_view()),
    path('rotation/<str:prep_id>', views.Rotation.as_view()),
    path('rotations', views.Rotations.as_view()),
    path('landmark_list',views.LandmarkList.as_view()),
    path('annotation_status',views.AnnotationStatus.as_view(),name = 'status')
]