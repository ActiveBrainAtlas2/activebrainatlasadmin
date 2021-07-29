from django.http import JsonResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth.models import User


class SessionVarView(TemplateView):
    def get(self, request, *args, **kwargs):
        data = {'user_id':0, 'username': None}
        if request.user.is_authenticated:
            result = request.user
            data = {'user_id':request.user.id, 'username': request.user.username}
        if settings.DEBUG:
            browser = str(request.META['HTTP_USER_AGENT']).lower()
            if 'firefox' in browser:
                id = 2
            else:
                id = 2
            user = User.objects.get(pk=id) 
            data = {'user_id':user.id, 'username': user.username}

        return JsonResponse(data)
