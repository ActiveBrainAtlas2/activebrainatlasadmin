import json
import numpy as np
from rest_framework import status
from django.test import Client, TransactionTestCase
from django.contrib.auth.models import User
# Create your tests here.
from brain.models import Animal, ScanRun
from neuroglancer.models import UrlModel, AnnotationPoints, BrainRegion, \
    InputType, LAUREN_ID
from neuroglancer.views import random_string
from random import uniform
import os
from datetime import datetime
import json


class TestUrlModel(TransactionTestCase):
    client = Client()

    def setUp(self):
        self.coms = [ 1,2,4,5,8,9,10,11,12,13,19,20,22,23,28,29,44,45,18,17,27,26]
        self.username = 'edward'
        self.animal_name = 'DKXX'
        self.atlas_name = 'Atlas'
        self.input_type_name = 'manual'
        self.label = random_string()
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
            self.scan_run = ScanRun.objects.create(prep_id=self.animal_name, 
                                                   resolution=0.325, zresolution=20,
                                                   number_of_slides=100)
        if query_set is not None and len(query_set) > 0:
            self.scan_run = query_set[0]

            
        # input type
        try:
            query_set = InputType.objects.filter(input_type=self.input_type_name)
        except InputType.DoesNotExist:
            self.input_type = InputType.objects.create(input_type=self.input_type_name)
        if query_set is not None and len(query_set) > 0:
            self.input_type = query_set[0]
        
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
        self.lauren.save()

    def test_neuroglancer_url(self):
        response = self.client.get("/neuroglancer")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rotations_url(self):
        response = self.client.get("/rotations")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_annotations_url(self):
        label = 'XXX'
        for com in self.coms:
            brain_region = BrainRegion.objects.get(pk=com)
            x1 = uniform(0, 65000)
            y1 = uniform(0, 35000)
            z1 = uniform(0, 450)
            try:
                p = AnnotationPoints.objects.create(animal=self.animal, brain_region=brain_region,
                    label=label, owner=self.owner, input_type=self.input_type,
                    x=x1, y=y1, z=z1)
            except Exception as e:
                print('could not create', e)
            try:
                p.save()
            except Exception as e:
                print('could not save', e)
        
        
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
            p = AnnotationPoints.objects.create(animal=self.animal, brain_region=self.brain_region,
                label='COM', owner=self.owner, input_type=self.input_type,
                x=x, y=y, z=z)
            p.save()
        
        c = AnnotationPoints.objects.count()
        self.assertGreaterEqual(c, n, msg=f'Error: Annotation point table has less than {n} entries.')
        
    def test_brain_region_count(self):
        n = BrainRegion.objects.count()
        self.assertGreater(n, 0, msg='Error: Brain region table is empty')

    
    def test_rotation_url_with_good_animal(self):
        for com in self.coms:
            brain_region = BrainRegion.objects.get(pk=com)
            x1 = uniform(0, 65000)
            y1 = uniform(0, 35000)
            z1 = uniform(0, 450)
            x2 = uniform(0, 55000)
            y2 = uniform(0, 45000)
            z2 = uniform(0, 350)
            p1 = AnnotationPoints.objects.create(animal=self.animal, brain_region=brain_region,
                label='COM', owner=self.owner, input_type=self.input_type,
                x=x1, y=y1, z=z1)
            p1.save()
            p2 = AnnotationPoints.objects.create(animal=self.atlas, brain_region=brain_region,
                label='COM', owner=self.lauren, input_type=self.input_type,
                x=x2, y=y2, z=z2)
            p2.save()
        qc = AnnotationPoints.objects.filter(animal=self.animal, label='COM', owner=self.owner).count()
        self.assertEqual(qc, len(self.coms), msg="Animal coms are of wrong size")
        
        
        url = f'/rotation/{self.animal_name}/{self.input_type_name}/{self.owner.id}'
        print(url)
        response = self.client.get(url)
        data = str(response.content, encoding='utf8')
        data = json.loads(data)
        translation = data['translation']
        s = np.sum(translation)
        #self.assertNotEqual(s, 0.0, msg="Translation is not equal to zero")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    
    def test_annotation_url(self):
        label = 'premotor'
        n = 10
        for i in range(n):
            x = uniform(0, 65000)
            y = uniform(0, 35000)
            z = uniform(0, 450)
            p = AnnotationPoints.objects.create(animal=self.animal, brain_region=self.brain_region,
                label=label, owner=self.owner, input_type=self.input_type,
                x=x, y=y, z=z)
            p.save()
        c = AnnotationPoints.objects\
            .filter(animal=self.animal)\
            .filter(label=label)\
            .filter(input_type=self.input_type)\
            .count()
        url = f'/annotation/{self.animal_name}/{label}/{self.input_type.id}'
        response = self.client.get(url)
        #self.assertGreater(len(response.data), c, msg="The number of annotations entered and returned do not match.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_annotation_Atlas_url(self):
        label = 'COM'
        AnnotationPoints.objects\
            .filter(animal=self.atlas)\
            .filter(label=label)\
            .filter(owner=self.lauren)\
            .filter(input_type=self.input_type)\
            .delete()
        for com in self.coms:
            brain_region = BrainRegion.objects.get(pk=com)
            x1 = uniform(0, 65000)
            y1 = uniform(0, 35000)
            z1 = uniform(0, 450)
            try:
                p = AnnotationPoints.objects.create(animal=self.atlas, brain_region=brain_region,
                    label=label, owner=self.lauren, input_type=self.input_type,
                    x=x1, y=y1, z=z1)
            except Exception as e:
                print('could not create', e)
            try:
                p.save()
            except Exception as e:
                print('could not save', e)
                
        qc = AnnotationPoints.objects\
            .filter(animal=self.atlas)\
            .filter(label=label)\
            .filter(owner=self.lauren)\
            .filter(input_type=self.input_type)\
            .count()
        self.assertEqual(qc, len(self.coms), msg="Atlas coms are of wrong size")

        url = f'/annotation/{self.atlas_name}/{label}/{self.input_type.id}'
        response = self.client.get(url)
        # self.assertGreater(len(response), 0, msg="Atlas coms are of wrong size")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_create_post_get_state(self):
        '''
        Ensure we can create a new neuroglancer_state object.
        neuroglancer_state is the new, url is the old
        owner_id is the new, person_id is the old
        '''
        parent_path = os.getcwd()
        jfile = f'{parent_path}/scripts/363.json'
        state = json.load(open(jfile))
        
        data = {}
        data['url'] = json.dumps(state)
        data['user_date'] = '999999'
        data['comments'] = self.label
        data['owner_id'] = self.owner.id
        data['created'] = datetime.now()
        data['updated'] =  datetime.now()
        
        response = self.client.post('/neuroglancer', data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print('ERROR', response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        urlModel = UrlModel.objects.filter(comments=self.label)
        n = UrlModel.objects.filter(comments=self.label).count()
        self.assertEqual(n, 1)
        self.assertEqual(urlModel[0].comments, self.label)
        self.state_id = urlModel[0].id
        
        response = self.client.get("/neuroglancer/" + str(self.state_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
