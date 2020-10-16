import json
from typing import List

from rest_framework import serializers
import logging
from neuroglancer.models import UrlModel, LayerData
from django.contrib.auth.models import User

logger = logging.getLogger('URLMODEL SERIALIZER LOGGING')

class UrlSerializer(serializers.ModelSerializer):
    person_id = serializers.IntegerField()

    class Meta:
        model = UrlModel
        #fields = ['id', 'animal', 'url', 'user_date', 'comments', 'person_id']
        fields = '__all__'
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

        #if 'annotations' in urlModel.url and 'point' in urlModel:
        #    structure_upsert(urlModel.id, urlModel.url)

        urlModel.url = None
        return urlModel

    def updateXXXX(self, instance, validated_data):
        pass
        instance.url = validated_data['url'],
        instance.user_date = validated_data['user_date'],
        instance.comments = validated_data['comments'],
        if 'person_id' in validated_data:
            try:
                authUser = User.objects.get(pk=validated_data['person_id'])
                instance.person = authUser
            except:
                logger.error('Person was not in validated data')

        try:
            instance.save()
        except:
            logger.error('Could not save url model')
        instance.url = None

        return instance

def structure_upsert(id, urldata):
    if urldata is not None:
        json_txt = json.loads(urldata)
        layers = json_txt['layers']
        for l in layers:
            if 'annotations' in l:
                name = l['name']
                annotation = l['annotations']
                rows = [row['point'] for row in annotation]
                #df = pd.DataFrame(rows, columns=['X', 'Y', 'Section'])
                #trunc = lambda x: math.trunc(x)
                #df = df.applymap(trunc)
                #df['Layer'] = name

            for row in rows:
                LayerData.objects.update_or_create(id=id, url_id=url)
