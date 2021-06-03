from django.urls import path, include
from neuroglancer import views 
from rest_framework import routers


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', views.UrlViewSet, basename='neuroglancer')
router.register(r'center', views.CenterOfMassViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(r'public', views.public_list, name='public'),
    path('annotation/<int:url_id>/<str:layer>', views.Annotation.as_view()),
    path('annotation/<str:prep_id>/<str:input_type>', views.Com.as_view()),
    path('annotations', views.Annotations.as_view()),
    path('rotation/<str:prep_id>/<str:input_type>/<int:person_id>', views.Rotation.as_view()),
    path('rotations', views.Rotations.as_view()),
    path('coms', views.CenterOfMassList.as_view()),
    path('ajax/load-layers/', views.load_layers, name='ajax_load_layers')
]