from rest_framework import serializers
from neuroglancer.models import UrlModel


class UrlSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UrlModel
        fields = ['url']
