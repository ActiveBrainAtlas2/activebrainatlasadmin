from neuroglancer.tasks import update_annotation_data
from rest_framework import serializers
from rest_framework.exceptions import APIException
import logging

from neuroglancer.models import AnnotationPoints, BrainRegion, UrlModel
from django.contrib.auth.models import User

logging.basicConfig()
logger = logging.getLogger(__name__)


class AnimalInputSerializer(serializers.Serializer):
    animal = serializers.CharField()


class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class AnnotationSerializer(serializers.Serializer):
    """
    This one feeds the data import
    """
    id = serializers.CharField()
    point = serializers.ListField()
    type = serializers.CharField()
    description = serializers.CharField()


class LineSerializer(serializers.Serializer):
    """
    This one feeds the data import
    """
    id = serializers.CharField()
    pointA = serializers.ListField()
    pointB = serializers.ListField()
    type = serializers.CharField()
    description = serializers.CharField()


class AnnotationsSerializer(serializers.Serializer):
    """
    This one feeds the dropdown
    """
    prep_id = serializers.CharField()
    label = serializers.CharField()
    input_type = serializers.CharField()
    input_type_id = serializers.IntegerField()


class BrainRegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrainRegion
        fields = '__all__'


class AnnotationPointsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnnotationPoints
        fields = '__all__'


class RotationModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source="person__username")

    class Meta:
        model = AnnotationPoints
        fields = ['animal', 'input_type_id', 'owner_id', 'username']


class RotationSerializer(serializers.Serializer):
    animal = serializers.CharField()
    input_type = serializers.CharField()
    owner_id = serializers.IntegerField()
    username = serializers.CharField()


class UrlSerializer(serializers.ModelSerializer):
    """Override method of entering a url into the DB.
    The url can't be in the UrlModel when it is returned
    to neuroglancer as it crashes neuroglancer."""
    owner_id = serializers.IntegerField()

    class Meta:
        model = UrlModel
        fields = '__all__'
        ordering = ['-created']

    def create(self, validated_data):
        """
        This gets called when a user clicks New in Neuroglancer
        """
        urlModel = UrlModel(
            url=validated_data['url'],
            user_date=validated_data['user_date'],
            comments=validated_data['comments'],
            public=False,
            vetted=False,
        )
        if 'owner_id' in validated_data:
            try:
                authUser = User.objects.get(pk=validated_data['owner_id'])
                urlModel.owner = authUser
            except User.DoesNotExist:
                logger.error('Person was not in validated data')
        try:
            urlModel.save()
        except APIException:
            logger.error('Could not save url model')
        update_annotation_data(urlModel)
        urlModel.url = None
        return urlModel

    def update(self, instance, validated_data):
        """
        This gets called when a user clicks Save in Neuroglancer
        """
        instance.url = validated_data.get('url', instance.url)
        instance.user_date = validated_data.get(
            'user_date', instance.user_date)
        instance.comments = validated_data.get('comments', instance.comments)
        if 'owner_id' in validated_data:
            try:
                authUser = User.objects.get(pk=validated_data['owner_id'])
                instance.owner = authUser
            except User.DoesNotExist:
                logger.error('Person was not in validated data')
        try:
            instance.save()
        except APIException:
            logger.error('Could not save url model')
        update_annotation_data(instance)
        instance.url = None
        return instance
