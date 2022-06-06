import json
import numpy as np
from rest_framework import status
from django.test import Client, TransactionTestCase
from django.contrib.auth.models import User
from brain.models import Animal, ScanRun
from neuroglancer.models import AnnotationSession, StructureCom, \
    MarkedCell, PolygonSequence, UrlModel, BrainRegion, LAUREN_ID 
from neuroglancer.views import random_string
from random import uniform
import os
from datetime import datetime


class TestUrlModel(TransactionTestCase):
    client = Client()

    def setUp(self):
        self.coms = [ 1,2,4,5,8,9,10,11,12,13,19,20,22,23,28,29,44,45,18,17,27,26]
        self.username = 'edward'
        self.annotator_username = 'zhongkai'
        self.prep_id = 'DK39'
        self.atlas_name = 'Atlas'
        self.annotation_type = 'POLYGON_SEQUENCE'
        self.label = random_string()
        # annotator
        try:
            query_set = User.objects.filter(username=self.annotator_username)
        except User.DoesNotExist:
            self.annotator = None
        if query_set is not None and len(query_set) > 0:
            self.annotator = query_set[0]
        else:
            self.annotator = User.objects.create(username=self.annotator_username,
                                                   email='super@email.org',
                                                   password='pass')
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
            
        try:
            self.lauren = User.objects.get(pk=LAUREN_ID)
        except User.DoesNotExist:
            self.lauren = User.objects.create(username='Lauren', email='l@here.com', password = 'pass', id = LAUREN_ID)

        self.lauren = User.objects.get(pk=LAUREN_ID)
        self.lauren.save()

        # atlas
        try:
            self.atlas = Animal.objects.get(pk=self.atlas_name)
        except Animal.DoesNotExist:
            self.atlas = Animal.objects.create(prep_id=self.atlas_name)
        
        # animal
        try:
            self.animal = Animal.objects.get(pk=self.prep_id)
        except Animal.DoesNotExist:
            self.animal = Animal.objects.create(prep_id=self.prep_id)
            
        try:
            query_set = ScanRun.objects.filter(prep_id=self.prep_id)
        except ScanRun.DoesNotExist:
            self.scan_run = ScanRun.objects.create(prep_id=self.prep_id, 
                                                   resolution=0.325, zresolution=20,
                                                   number_of_slides=100)
        if query_set is not None and len(query_set) > 0:
            self.scan_run = query_set[0]
        # brain_region    
        try:
            query_set = BrainRegion.objects.filter(abbreviation='point')
        except BrainRegion.DoesNotExist:
            self.brain_region = None
        if query_set is not None and len(query_set) > 0:
            self.brain_region = query_set[0]
        else:
            self.brain_region = BrainRegion.objects.create(abbreviation='point', color=1)

        
        # annotation session brain
        query_set = AnnotationSession.objects \
            .filter(animal=self.animal)\
            .filter(brain_region=self.brain_region)\
            .filter(annotator=self.annotator)\
            .filter(annotation_type=self.annotation_type)

        if query_set is not None and len(query_set) > 0:
            self.annotation_session = query_set[0]
        else:
            self.annotation_session = AnnotationSession.objects.create(\
                animal=self.animal,
                brain_region=self.brain_region,
                annotator=self.lauren,
                annotation_type=self.annotation_type
                )
        
        # annotation session brain
        query_set = AnnotationSession.objects \
            .filter(animal=self.animal)\
            .filter(brain_region=self.brain_region)\
            .filter(annotator=self.annotator)\
            .filter(annotation_type=self.annotation_type)

        if query_set is not None and len(query_set) > 0:
            self.annotation_session = query_set[0]
        else:
            self.annotation_session = AnnotationSession.objects.create(\
                animal=self.animal,
                brain_region=self.brain_region,
                annotator=self.lauren,
                annotation_type=self.annotation_type
                )

        # annotation session polygon sequence
        query_set = AnnotationSession.objects \
            .filter(animal=self.atlas)\
            .filter(brain_region=self.brain_region)\
            .filter(annotator=self.annotator)\
            .filter(annotation_type=self.annotation_type)

        if query_set is not None and len(query_set) > 0:
            self.annotation_session_polygon_sequence = query_set[0]
        else:
            self.annotation_session_polygon_sequence = AnnotationSession.objects.create(\
                animal=self.atlas,
                brain_region=self.brain_region,
                annotator=self.annotator,
                annotation_type=self.annotation_type
                )


    def test_01_neuroglancer_url(self):
        """tests the API that returns the list of available neuroglancer states
        """
        response = self.client.get("/neuroglancer")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """URLs take from neuroglancer/urls.py We should have one test per url
        transformation_relate_urls 
            path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/'
            path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<int:reverse>'
            path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<str:reference_scales>'
            path('rotation/<str:prep_id>/<str:input_type>/<int:owner_id>/<int:reverse>/<str:reference_scales>'
            path('rotations'
        volume_related_urls 
            path('get_volume/<str:session_id>'
            path('get_volume_list'
            path('contour_to_segmentation/<int:url_id>/<str:volume_id>'
        general_urls = 
            path(r'public'
            path('landmark_list'
            path('annotation_status'
            path('save_annotations/<int:url_id>/<str:annotation_layer_name>'
        com_related_urls = 
            path('get_com/<str:prep_id>/<str:annotator_id>/<str:source>'
            path('get_com_list'
        marked_cell_related_urls = [
            path('get_marked_cell/<str:session_id>'
            path('get_marked_cell_list'
            path('cell_types'
    """
    '''
    def test_02_rotations(self):
        """Test the API that returns the list of available transformations
        TODO fix this, it does not work
        """
        response = self.client.get(f"/rotation/{self.prep_id}/{self.input_type}/{self.owner.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_03_rotations(self):
        """Test the API that returns the list of available transformations
        TODO fix this, it does not work
        """
        response = self.client.get(f"/rotation/{self.prep_id}/{self.input_type}/{self.owner.id}/{self.reverse}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_04_rotations(self):
        """Test the API that returns the list of available transformations
        TODO fix this, it does not work
        """
        response = self.client.get(f"/rotation/{self.prep_id}/{self.input_type}/{self.owner.id}/{self.reference_scales}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_05_rotations(self):
        """Test the API that returns the list of available transformations
        TODO fix
        """
        response = self.client.get(f"/rotation/{self.prep_id}/{self.input_type}/{self.owner.id}/{self.reverse}/{self.reference_scales}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    '''
    def test_06_rotations(self):
        """Test the API that returns the list of available transformations
         This one works
        """
        response = self.client.get("/rotations")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    '''
    def test_07_get_volume(self):
        """Test the API that returns a volume
        TODO fix, it does not work
        """
        
        response = self.client.get(f"/get_volume/{self.annotation_session_polygon_sequence.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
          
    def test_08_get_volume_list(self):
        """Test the API that returns the list of volumes
        TODO fix
        """
        response = self.client.get(f"/get_volume_list")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

     def test_09_contour_to_segmentation(self):
        """Test the API that returns contour to segmentation
        TODO fix
        """
        response = self.client.get(f"/contour_to_segmentation")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_03_annotations_url(self):
        """Test fetching annotations. 
        """
        source = StructureCom.SourceChoices.MANUAL
        for com in self.coms:
            x1 = uniform(0, 65000)
            y1 = uniform(0, 35000)
            z1 = uniform(0, 450)
            try:
                StructureCom.objects.create(annotation_session=self.annotation_session,
                    source=source, 
                    x=x1, y=y1, z=z1)
            except Exception as e:
                print('could not create', e)
        
        
        response = self.client.get("/save_annotations")
        print(response)
        #self.assertGreater(len(response.data), 0, msg="The number of annotations should be greater than 0.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_04_rotation_url_with_bad_animal(self):
        """Test the API that retrieves a specific transformation for a nonexistant animal and checks that the identity transform is returned
        """
        response = self.client.get("/rotation/DK52XXX")
        data = str(response.content, encoding='utf8')
        data = json.loads(data)
        translation = data['translation']
        s = np.sum(translation)
        self.assertEqual(s, 0, msg="Translation is equal to zero")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_05_create_structure_com(self):
        """Test the API that retrieves a specific transformation for a nonexistant animal and checks that the identity transform is returned
        """
        n = 10
        for _ in range(n):
            x = uniform(0, 65000)
            y = uniform(0, 35000)
            z = uniform(0, 450)
            p = StructureCom.objects.create(annotation_session=self.annotation_session,
                label='COM', x=x, y=y, z=z)
            p.save()
        
        c = StructureCom.objects.count()
        self.assertGreaterEqual(c, n, msg=f'Error: Structure COM table has less than {n} entries.')
        
    def test_06_brain_region_count(self):
        n = BrainRegion.objects.count()
        self.assertGreater(n, 0, msg='Error: Brain region table is empty')

    
    def test_07_rotation_url_with_good_animal(self):
        url = f'/rotation/{self.animal.prep_id}'
        print('url is ', url)
        response = self.client.get(url)
        data = str(response.content, encoding='utf8')
        data = json.loads(data)
        translation = data['translation']
        s = np.sum(translation)
        # self.assertNotEqual(s, 0.0, msg="Translation is not equal to zero")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    
    def test_08_annotation_markedcell_url(self):
        label = 'premotor'
        n = 10
        for _ in range(n):
            x = uniform(0, 65000)
            y = uniform(0, 35000)
            z = uniform(0, 450)
            p = MarkedCell.objects.create(annotation_session=self.annotation_session,
                label=label, x=x, y=y, z=z)
            p.save()
        c = MarkedCell.objects\
            .filter(annotation_session=self.annotation_session)\
            .filter(label=label)\
            .count()
        url = f'/annotation/MarkedCell/{self.prep_id}/{label}'
        response = self.client.get(url)
        self.assertGreaterEqual(len(response.data), c, msg="The number of annotations entered and returned do not match.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_09_annotation_Atlas_url(self):
        label = 'COM'
        StructureCom.objects\
            .filter(annotation_session__animal=self.atlas)\
            .filter(label=label)\
            .delete()
        n = 10
        for _ in range(n):
            x1 = uniform(0, 65000)
            y1 = uniform(0, 35000)
            z1 = uniform(0, 450)
            try:
                p = StructureCom.objects.create(annotation_session=self.annotation_session_atlas,
                    label=label, x=x1, y=y1, z=z1)
            except Exception as e:
                print('could not create', e)
            try:
                p.save()
            except Exception as e:
                print('could not save', e)
                
        qc = StructureCom.objects\
            .filter(annotation_session=self.annotation_session_atlas)\
            .filter(label=label)\
            .count()
        self.assertEqual(qc, n, msg="Atlas coms are of wrong size")

        url = f'/annotation/MarkedCell/{self.atlas_name}/{label}'
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0, msg="Atlas coms are of wrong size")

    '''