from django.conf.urls import url
from django.urls import path
from workflow.views import progress_test, get_progress, progress_view
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tasks.html')),
    path(r'progress', progress_view, name='progress'),
    path(r'progress_test', progress_test, name='progress_test'),
    path('<int:task_id>', get_progress, name='task_status'),
]
