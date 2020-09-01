from rest_framework import serializers
import logging
from neuroglancer.models import UrlModel
from django.contrib.auth.models import User

logger = logging.getLogger('URLMODEL SERIALIZER LOGGING')

class UrlSerializer(serializers.HyperlinkedModelSerializer):
    person_id = serializers.IntegerField()

    class Meta:
        model = UrlModel
        fields = ['animal', 'url', 'user_date', 'comments', 'person_id']
        ordering = ['-created']


    def create(self, validated_data):
        logger.info('Creating url')
        urlModel = UrlModel(
            url=validated_data['url'],
            user_date=validated_data['user_date'],
            comments=validated_data['comments'],
            public = False,
            vetted = False,
        )
        if 'person_id' in validated_data:
            try:
                authUser = User.objects.get(pk=validated_data['person_id'])
                urlModel.person = authUser
            except:
                logger.error('Person was not in validated data')

        try:
            urlModel.save()
        except:
            logger.error('Could not save url model')
        return UrlModel()
