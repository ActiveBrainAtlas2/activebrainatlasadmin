from django.http import HttpResponse
from django.views.generic import TemplateView


class SessionVarView(TemplateView):
    def get(self, request, *args, **kwargs):
        result = "not"
        if request.user.is_authenticated:
            result = request.user.username
        return HttpResponse(result)
