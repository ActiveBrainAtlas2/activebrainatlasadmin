from rest_framework import viewsets
from rest_framework import permissions

from django.shortcuts import render

from neuroglancer.serializers import UrlSerializer
from neuroglancer.models import UrlModel

class UrlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UrlModel.objects.all().order_by('-created')
    serializer_class = UrlSerializer
    permission_classes = [permissions.AllowAny]
