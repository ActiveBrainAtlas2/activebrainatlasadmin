import json
from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import APIException

import logging

from brain.models import Animal
from neuroglancer.models import UrlModel, LayerData, CenterOfMass, Structure
from django.contrib.auth.models import User

logging.basicConfig()
logger = logging.getLogger(__name__)


def update_center_of_mass(urlModel):
    try:
        json_txt = json.loads(urlModel.url)
    except ValueError as e:
        print('Loading json from url failed', e)
        return
    if 'layers' in json_txt:
        layers = json_txt['layers']
        for layer in layers:
            if 'annotations' in layer:
                lname = layer['name']
                if 'com' in lname.lower():
                    annotation = layer['annotations']
                    for com in annotation:
                        x = com['point'][0]
                        y = com['point'][1]
                        z = com['point'][2]
                        if 'description' in com:
                            abbreviation = str(com['description']).replace('\n','').strip()
                            try:
                                structure = Structure.objects.get(abbreviation=abbreviation)
                            except Structure.DoesNotExist:
                                logger.error("Structure does not exist")

                            try:
                                prep = Animal.objects.get(pk=urlModel.animal)
                            except Animal.DoesNotExist:
                                logger.error("Animal does not exist")

                            if structure is not None and prep is not None:
                                CenterOfMass.objects.update_or_create(
                                    prep=prep, structure=structure,
                                    defaults={
                                        "x": x,
                                        "y": y,
                                        "section": z,
                                        "active": True,
                                        "created": datetime.now()
                                    }
                                )

class UrlSerializer(serializers.ModelSerializer):
    """Override method of entering a url into the DB.
    The url can't be in the UrlModel when it is returned
    to neuroglancer as it crashes neuroglancer."""
    person_id = serializers.IntegerField()

    class Meta:
        model = UrlModel
        fields = '__all__'
        ordering = ['-created']


    def create(self, validated_data):
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

        update_center_of_mass(urlModel)

        urlModel.url = None
        return urlModel

    def update(self, instance, validated_data):
        instance.url = validated_data.get('url', instance.url)
        instance.user_date = validated_data.get('user_date', instance.user_date)
        instance.comments = validated_data.get('comments', instance.comments)

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

        update_center_of_mass(instance)

        instance.url = None
        return instance




class StructureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Structure
        fields = '__all__'


class CenterOfMassSerializer(serializers.ModelSerializer):
    """Takes care of entering a set of points"""
    structure_id = serializers.CharField()

    class Meta:
        model = CenterOfMass
        fields = '__all__'

    def create(self, validated_data):
        logger.debug('Creating COM')
        com = CenterOfMass(
            x=validated_data['x'],
            y=validated_data['y'],
            section=validated_data['section'],
            active = True,
            created = datetime.now()
        )
        try:
            structure = Structure.objects.get(abbreviation__exact=validated_data['structure_id'])
            com.structure = structure
        except APIException as e:
            logger.error(f'Error with structure {e}')

        try:
            prep = Animal.objects.get(prep_id=validated_data['prep'])
            com.prep = prep
        except:
            logger.error('Error with animal')
        try:
            com.save()
        except APIException as e:
            logger.error(f'Could not save center of mass: {e}')

        return com

