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
from neuroglancer.views import UrlViewSet
#router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)
#router.register(r'locations', views.LocationViewSet)
#router.register(r'schedules', views.ScheduleViewSet)
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', UrlViewSet)



urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'image-listing', brain_views.image_list),
    path(r'graph', gantt),
    path(r'gantt', TemplateView.as_view(template_name='gantt.html')),
    #path('', include(router.urls)),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #path(r'api-token-auth/', obtain_jwt_token),
    #path(r'api-token-refresh/', refresh_jwt_token),
    #path(r'oauth/', include('social_django.urls', namespace='social')),
    path(r'session', SessionVarView.as_view(), name='session-var'),
    # cvat stuff
    #path('', include('cvat.apps.engine.urls')),
]

if apps.is_installed('cvat.apps.engine'):
    import cvat
    from cvat.apps.engine import views as eviews
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    from cvat.apps.restrictions.views import RestrictionsViewSet

    urlpatterns.append(path('django-rq/', include('django_rq.urls'))),
    urlpatterns.append(path('auth/', include('cvat.apps.authentication.urls'))),
    urlpatterns.append(path('documentation/', include('cvat.apps.documentation.urls'))),

    schema_view = get_schema_view(
       openapi.Info(
          title="CVAT REST API",
          default_version='v1',
          description="REST API for Computer Vision Annotation Tool (CVAT)",
          terms_of_service="https://www.google.com/policies/terms/",
          contact=openapi.Contact(email="nikita.manovich@intel.com"),
          license=openapi.License(name="MIT License"),
       ),
       public=True,
       permission_classes=(permissions.IsAuthenticated,),
    )

    router.register('projects', eviews.ProjectViewSet)
    router.register('tasks', eviews.TaskViewSet)
    router.register('jobs', eviews.JobViewSet)
    router.register('users', eviews.UserViewSet)
    router.register('server', eviews.ServerViewSet, basename='server')
    router.register('plugins', eviews.PluginViewSet)
    router.register('restrictions', RestrictionsViewSet, basename='restrictions')

    urlpatterns += [
        # Entry point for a client
        path('', include(router.urls)),
        #path('', eviews.dispatch_request),
        path('dashboard/', eviews.dispatch_request),

        # documentation for API
        path('api/swagger<str:scheme>', eviews.wrap_swagger(
           schema_view.without_ui(cache_timeout=0)), name='schema-json'),
        path('api/swagger/', eviews.wrap_swagger(
           schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
        path('api/docs/', eviews.wrap_swagger(
           schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),

        # entry point for API
        path('api/v1/auth/', include('cvat.apps.authentication.api_urls')),
        path('api/v1/', include((router.urls, 'cvat'), namespace='v1'))
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

urlpatterns += [ path('', include(router.urls)),]
