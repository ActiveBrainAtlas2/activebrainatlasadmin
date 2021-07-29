from django.urls import path, include
from neuroglancer import views 
from rest_framework import routers


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', views.UrlViewSet, basename='neuroglancer')

urlpatterns = [
    path('', include(router.urls)),
    path(r'public', views.public_list, name='public'),
    path('annotation/<str:prep_id>/<str:layer_name>/<int:input_type_id>', views.Annotation.as_view()),
    path('annotations', views.Annotations.as_view()),
    path('rotation/<str:prep_id>/<str:input_type>/<int:person_id>', views.Rotation.as_view()),
    path('rotations', views.Rotations.as_view()),
    path('ajax/load-layers/', views.load_layers, name='ajax_load_layers')
]