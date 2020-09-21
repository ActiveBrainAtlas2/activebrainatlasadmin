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
from django.apps import apps
from activebrainatlas.views import SessionVarView
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

admin.autodiscover()


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'image-listing', brain_views.image_list),
    path(r'graph', gantt),
    path(r'gantt', TemplateView.as_view(template_name='gantt.html')),
    path('', include(router.urls)),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #path(r'api-token-auth/', obtain_jwt_token),
    #path(r'api-token-refresh/', refresh_jwt_token),
    #path(r'oauth/', include('social_django.urls', namespace='social')),
    path(r'session', SessionVarView.as_view(), name='session-var'),
    # cvat stuff
    path('', include('cvat.apps.engine.urls')),
    path('django-rq/', include('django_rq.urls')),
    path('auth/', include('cvat.apps.authentication.urls')),
    path('documentation/', include('cvat.apps.documentation.urls')),
]


if apps.is_installed('cvat.apps.tf_annotation'):
    urlpatterns.append(path('tensorflow/annotation/', include('cvat.apps.tf_annotation.urls')))

if apps.is_installed('cvat.apps.git'):
    urlpatterns.append(path('git/repository/', include('cvat.apps.git.urls')))

if apps.is_installed('cvat.apps.reid'):
    urlpatterns.append(path('reid/', include('cvat.apps.reid.urls')))

if apps.is_installed('cvat.apps.auto_annotation'):
    urlpatterns.append(path('auto_annotation/', include('cvat.apps.auto_annotation.urls')))

if apps.is_installed('cvat.apps.dextr_segmentation'):
    urlpatterns.append(path('dextr/', include('cvat.apps.dextr_segmentation.urls')))

if apps.is_installed('cvat.apps.log_viewer'):
    urlpatterns.append(path('analytics/', include('cvat.apps.log_viewer.urls')))

if apps.is_installed('silk'):
    urlpatterns.append(path('profiler/', include('silk.urls')))

# new feature by Mohammad
if apps.is_installed('cvat.apps.auto_segmentation'):
    urlpatterns.append(path('tensorflow/segmentation/', include('cvat.apps.auto_segmentation.urls')))



#if DEBUG:
#    from django.conf.urls.static import static
#    urlpatterns = urlpatterns + static(MEDIA_URL, document_root=MEDIA_ROOT)
