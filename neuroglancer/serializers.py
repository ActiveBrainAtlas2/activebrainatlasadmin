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

class PolygonSerializer(serializers.Serializer):
    source = serializers.ListField(required=False)
    pointA = serializers.ListField(required=False)
    pointB = serializers.ListField(required=False)
    childAnnotationIds = serializers.ListField(required=False)
    id = serializers.CharField()
    type = serializers.CharField()
    parentAnnotationId = serializers.CharField(required=False)
    props = serializers.ListField()
    description = serializers.CharField(required=False)

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
    prep_id = serializers.CharField()
    input_type = serializers.CharField()
    owner_id = serializers.IntegerField()
    username = serializers.CharField()


class UrlSerializer(serializers.ModelSerializer):
    """Override method of entering a url into the DB.
    The url *probably* can't be in the UrlModel when it is returned
    to neuroglancer as it crashes neuroglancer."""

    class Meta:
        model = UrlModel
        fields = '__all__'
        ordering = ['-created']

    def create(self, validated_data):
        """
        This gets called when a user clicks New in Neuroglancer
        """
        obj = UrlModel(
            url=validated_data['url'],
            user_date=validated_data['user_date'],
            comments=validated_data['comments'],
        )
        if 'owner' in validated_data:
            owner = validated_data['owner']
            obj = self.take_care_of_owner(obj, owner)
        return obj

    def update(self, obj, validated_data):
        """
        This gets called when a user clicks Save in Neuroglancer
        """
        obj.url = validated_data.get('url', obj.url)
        obj.user_date = validated_data.get('user_date', obj.user_date)
        obj.comments = validated_data.get('comments', obj.comments)
        if 'owner' in validated_data:
            owner = validated_data['owner']
            obj = self.take_care_of_owner(obj, owner)
        return obj

    def take_care_of_owner(self, obj, owner):
        '''
        Takes care of tasks that are in both create and update
        :param obj: the neuroglancerModel object
        :param owner: the owner object from the validated_data
        '''
        try:
            # authUser = User.objects.get(pk=owner)
            obj.owner = owner
        except User.DoesNotExist:
            logger.error('Owner was not in validated data')
        try:
            obj.save()
        except APIException:
            logger.error('Could not save Neuroglancer model')
        update_annotation_data(obj)
        obj.url = None
        return obj
