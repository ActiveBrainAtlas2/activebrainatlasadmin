from django.http import JsonResponse
from django.views.generic import TemplateView


class SessionVarView(TemplateView):
    def get(self, request, *args, **kwargs):
        result = 0
        if request.user.is_authenticated:
            result = request.user.id
        data = {'person_id':result}
        return JsonResponse(data)
