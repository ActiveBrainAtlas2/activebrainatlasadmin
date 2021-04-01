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
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from activebrainatlas.views import SessionVarView
from workflow.gantt_view import gantt

from rest_framework import routers
from neuroglancer.views import UrlViewSet, CenterOfMassViewSet, AlignAtlasView, UrlDataView
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'neuroglancer', UrlViewSet, basename='neuroglancer')
router.register(r'center', CenterOfMassViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'graph', gantt),
    path(r'gantt', TemplateView.as_view(template_name='gantt.html')),
    path(r'session', SessionVarView.as_view(), name='session-var'),
    path(r'alignatlas', AlignAtlasView.as_view(), name='align-atlas'),
    path(r'urldata', UrlDataView.as_view(), name='get-data'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('', include('brain.urls')),
    path('', include('neuroglancer.urls')),
]

# drf-yasg component doesn't handle correctly URL_FORMAT_OVERRIDE and
# send requests with ?format=openapi suffix instead of ?scheme=openapi.
# We map the required paramater explicitly and add it into query arguments
# on the server side.
def wrap_swagger(view):
    @login_required
    def _map_format_to_schema(request, scheme=None):
        if 'format' in request.GET:
            request.GET = request.GET.copy()
            format_alias = settings.REST_FRAMEWORK['URL_FORMAT_OVERRIDE']
            request.GET[format_alias] = request.GET['format']

        return view(request, format=scheme)

    return _map_format_to_schema


if apps.is_installed('cvat.apps.authentication'):
    from cvat.apps.authentication.decorators import login_required
    from cvat.apps.engine import views as eviews
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    from cvat.apps.restrictions.views import RestrictionsViewSet

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
    router.register('restrictions', RestrictionsViewSet, basename='restrictions')
    urlpatterns += [
        # Entry point for a client
        path('', RedirectView.as_view(url=settings.UI_URL, permanent=True,
                                      query_string=True)),

        # documentation for API
        path('api/swagger<str:scheme>', wrap_swagger(
            schema_view.without_ui(cache_timeout=0)), name='schema-json'),
        path('api/swagger/', wrap_swagger(
            schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
        path('api/docs/', wrap_swagger(
            schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),

        # entry point for API
        path('api/v1/auth/', include('cvat.apps.authentication.urls')),
        path('api/v1/', include((router.urls, 'cvat'), namespace='v1'))
    ]

#if DEBUG:
#    from django.conf.urls.static import static
#    urlpatterns = urlpatterns + static(MEDIA_URL, document_root=MEDIA_ROOT)

urlpatterns += [ path('', include(router.urls)),]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
