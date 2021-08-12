import json
from rest_framework import status
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
# Create your tests here.
from neuroglancer.models import UrlModel

class TestUrlModel(TransactionTestCase):
    client = Client()

    def setUp(self):
        super_user = User.objects.create_superuser(username='super', email='super@email.org', password='pass')
        # ids 168, 188,210,211,209,200
        id = 273
        self.urlModel = UrlModel.objects.get(pk=id)

        self.serializer_data = {
            'url': self.urlModel.url,
            'user_date': self.urlModel.user_date,
            'comments': self.urlModel.comments,
            'person_id': super_user.id
        }

        self.bad_serializer_data = {
            'url': None,
            'user_date': None,
            'comments': None,
            'vetted': None,
            'public': None,
            'person_id': "18888888888"
        }

    def test_neuroglancer_url(self):
            response = self.client.get("/neuroglancer")
            request = response.wsgi_request
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rotations_url(self):
            response = self.client.get("/rotations")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_annotations_url(self):
            response = self.client.get("/annotations")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rotation_url(self):
            response = self.client.get("/rotation/DK52/manual/2")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_annotation_url(self):
            response = self.client.get("/annotation/DK39/premotor/1")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_annotation_Atlas_url(self):
            response = self.client.get("/annotation/Atlas/COM/1")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
