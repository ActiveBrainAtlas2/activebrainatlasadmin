import json
import numpy as np
from rest_framework import status
from django.test import Client, TransactionTestCase
from django.contrib.auth.models import User
# Create your tests here.
from brain.models import Animal, ScanRun
from neuroglancer.models import UrlModel, AnnotationPoints, BrainRegion, \
    InputType, LAUREN_ID
from random import uniform


class TestUrlModel(TransactionTestCase):
    client = Client()

    def setUp(self):
        self.username = 'edward'
        self.animal_name = 'DKXX'
        self.atlas_name = 'Atlas'
        self.input_type_name = 'manual'
        # atlas
        try:
            self.atlas = Animal.objects.get(pk=self.atlas_name)
        except Animal.DoesNotExist:
            self.atlas = Animal.objects.create(prep_id=self.atlas_name)
        # animal
        try:
            self.animal = Animal.objects.get(pk=self.animal_name)
        except Animal.DoesNotExist:
            self.animal = Animal.objects.create(prep_id=self.animal_name)
            
        try:
            query_set = ScanRun.objects.filter(prep_id=self.animal_name)
        except ScanRun.DoesNotExist:
            self.scan_run = None
        if query_set is not None and len(query_set) > 0:
            self.scan_run = query_set[0]
        else:
            self.scan_run = ScanRun.objects.create(prep_id=self.animal_name, 
                                                   resolution=0.325, zresolution=20,
                                                   number_of_slides=100)

            
        # input type
        try:
            query_set = InputType.objects.filter(input_type=self.input_type_name)
        except InputType.DoesNotExist:
            self.input_type = None
        if query_set is not None and len(query_set) > 0:
            self.input_type = query_set[0]
        else:
            self.input_type = InputType.objects.create(input_type=self.input_type_name)
        
        # brain_region    
        try:
            query_set = BrainRegion.objects.filter(abbreviation='point')
        except BrainRegion.DoesNotExist:
            self.brain_region = None
        if query_set is not None and len(query_set) > 0:
            self.brain_region = query_set[0]
        else:
            self.brain_region = BrainRegion.objects.create(abbreviation='point', color=1)

        # User            
        try:
            query_set = User.objects.filter(username=self.username)
        except User.DoesNotExist:
            self.owner = None
        if query_set is not None and len(query_set) > 0:
            self.owner = query_set[0]
        else:
            self.owner = User.objects.create(username=self.username,
                                                   email='super@email.org',
                                                   password='pass')
            
        # ids 168, 188,210,211,209,200
        
        try:
            self.lauren = User.objects.get(pk=LAUREN_ID)
        except User.DoesNotExist:
            self.lauren = User.objects.create(username='Lauren', email='l@here.com', password = 'pass', id = LAUREN_ID)

        self.lauren = User.objects.get(pk=LAUREN_ID)

        pk = 273
        self.urlModel = UrlModel.objects.get(pk=pk)

        self.serializer_data = {
            'url': self.urlModel.url,
            'user_date': self.urlModel.user_date,
            'comments': self.urlModel.comments,
            'owner_id': self.owner.id
        }

        self.bad_serializer_data = {
            'url': None,
            'user_date': None,
            'comments': None,
            'vetted': None,
            'public': None,
            'owner_id': "18888888888"
        }

    def test_neuroglancer_url(self):
        response = self.client.get("/neuroglancer")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rotations_url(self):
        response = self.client.get("/rotations")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_annotations_url(self):
        response = self.client.get("/annotations")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rotation_url_with_bad_animal(self):
        response = self.client.get("/rotation/DK52XXX/manual/2")
        data = str(response.content, encoding='utf8')
        data = json.loads(data)
        translation = data['translation']
        s = np.sum(translation)
        self.assertEqual(s, 0, msg="Translation is equal to zero")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_annotation(self):
        n = 10
        for i in range(n):
            x = uniform(0, 65000)
            y = uniform(0, 35000)
            z = uniform(0, 450)
            AnnotationPoints.objects.create(animal=self.animal, brain_region=self.brain_region,
                label='COM', owner=self.owner, input_type=self.input_type,
                x=x, y=y, z=z)
        
        
        n = AnnotationPoints.objects.count()
        print('count of points is ', n)
        self.assertGreater(n, 0, msg='Error: Annotation point table is empty')
        
    def test_brain_region_count(self):
        n = BrainRegion.objects.count()
        print('count of brain regions is ', n)
        self.assertGreater(n, 0, msg='Error: Brain region table is empty')

    
    def test_rotation_url_with_good_animal(self):
        coms = [ 1,2,4,5,8,9,10,11,12,13,19,20,22,23,28,29,44,45,18,17,27,26]
        for com in coms:
            brain_region = BrainRegion.objects.get(pk=com)
            x1 = uniform(0, 65000)
            y1 = uniform(0, 35000)
            z1 = uniform(0, 450)
            x2 = uniform(0, 65000)
            y2 = uniform(0, 35000)
            z2 = uniform(0, 450)
            AnnotationPoints.objects.create(animal=self.animal, brain_region=brain_region,
                label='COM', owner=self.owner, input_type=self.input_type,
                x=x1, y=y1, z=z1)
            AnnotationPoints.objects.create(animal=self.atlas, brain_region=brain_region,
                label='COM', owner=self.lauren, input_type=self.input_type,
                x=x2, y=y2, z=z2)

        qc = AnnotationPoints.objects.filter(animal=self.animal, label='COM', owner=self.owner).count()
        print(f'count of {self.animal_name} COMs is {qc}')
        
        qc = AnnotationPoints.objects.filter(animal=self.atlas).filter(label='COM').count()
        print(f'count of {self.atlas_name} COMs is {qc}')
        
        url = f'/rotation/{self.animal_name}/{self.input_type_name}/{self.owner.id}'
        print('url is', url)    
        response = self.client.get(url)
        data = str(response.content, encoding='utf8')
        data = json.loads(data)
        translation = data['translation']
        s = np.sum(translation)
        print(data)
        self.assertNotEqual(s, 0.0, msg="Translation is not equal to zero")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    """
    def test_annotation_url(self):
        response = self.client.get("/annotation/DK39/premotor/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_annotation_Atlas_url(self):
        response = self.client.get("/annotation/Atlas/COM/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    """
