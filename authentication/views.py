from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.conf import settings

from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
import authentication
from django.contrib import messages

from rest_framework import generics, viewsets
from rest_framework import permissions
from rest_framework.response import Response

from authentication.models import Lab, User
from authentication.serializers import LabSerializer, RegisterSerializer, \
    UserSerializer, ValidateUserSerializer

"""
def account_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authentication(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect(reverse('your_success_url'))
        else:
            messages.error(request,'username or password not correct')
            return redirect(reverse('your_login_url'))
        
                
    else:
        form = AuthenticationForm()
    return render(request,'your_template_name.html',{'form':form})
"""

class LabViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the neuroglancer states to be viewed or edited.
    Note, the update, and insert methods are over ridden in the serializer.
    It was more convienent to do them there than here.
    """
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RegisterView(generics.CreateAPIView):
    """
    Description of RegisterView
    This is when a person registers to become a user on the registration page. 
    This must be allowed to accept posts so
    we allow unauthenticated access

    Inheritance:
        generics.CreateAPIView:

    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class SessionVarViewDEPRECATED(generics.ListAPIView):
    '''
    This has been deprecated and replaced by using cookies 
    which the angular front end and the neuroglancer program both can use. 
    This gets the session var from Neuroglancer to check
    if the user is logged in. Note, this works fine on the
    production server, but since Neuroglancer and Django
    run on different ports locally, it is a pain to translate
    between the two. To test Neuroglancer locally:
        for login, comment out the if statement,
        when you do this, the user will ALWAYS appear to be not logged in! This
        is because of the different ports!!!!!!!!!!!!!!!!!!!!!!!!!!!
    '''

    def get(self, request, *args, **kwargs):
        user = {'id':0, 'username':''}
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.id) 
            # data = {'user_id':user.id, 'username': user.username}
        
        if settings.DEBUG:
            userid = 1
            browser = str(request.META['HTTP_USER_AGENT']).lower()
            if 'firefox' in browser:
                userid = 2
            user = User.objects.get(pk=userid) 
            # data = {'user_id':user.id, 'username': user.username}
        
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


class UserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, username):
        user = {'id':0}
        try:
           queryset = User.objects.filter(username=username)
        except User.DoesNotExist:
            raise Http404
        if queryset is not None and len(queryset) > 0:
            user = queryset[0]

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


class ValidateUserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ValidateUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = User.objects.all()
        username = self.request.query_params.get('username')
        if username is not None:
            return queryset.filter(username=username)

        email = self.request.query_params.get('email')
        if email is not None:
            return queryset.filter(email=email)

        return User.objects.filter(pk=0)
