from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from neuroglancer import views

urlpatterns = [
    path(r'public', views.public_list, name='public'),
    path('annotations', views.AnnotationList.as_view()),
    path('annotation/<int:pk>/<str:layer_name>', views.PointList.as_view()),
]