from rest_framework import viewsets
from rest_framework import permissions


from neuroglancer.serializers import UrlSerializer
from neuroglancer.models import UrlModel

class UrlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UrlModel.objects.all()
    serializer_class = UrlSerializer
    permission_classes = [permissions.AllowAny]
    # lookup_field = "id"

