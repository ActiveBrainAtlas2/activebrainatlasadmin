"""activebrainatlas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from brain import views as brain_views
from workflow.gantt_view import gantt

from rest_framework import routers
from scheduler import views
from neuroglancer import views as neuroviews
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'neuroglancer', neuroviews.UrlViewSet)
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
#from .settings import DEBUG, MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'image-listing', brain_views.image_list),
    path(r'graph', gantt),
    path(r'gantt', TemplateView.as_view(template_name='gantt.html')),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'api-token-auth/', obtain_jwt_token),
    path(r'api-token-refresh/', refresh_jwt_token),
    path(r'oauth/', include('social_django.urls', namespace='social')),
]
#if DEBUG:
#    from django.conf.urls.static import static
#    urlpatterns = urlpatterns + static(MEDIA_URL, document_root=MEDIA_ROOT)
