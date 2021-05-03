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


    def test_create_invalid(self):
        """
        should be a failed insert
        test inserting bad data
        :return:
        """
        response = self.client.post(
            reverse('neuroglancer-list'),
            data=json.dumps(self.bad_serializer_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_valid(self):
        """
        1st insert
        test inserting good data
        :return:
        """
        response = self.client.post(
            reverse('neuroglancer-list'),
            data=json.dumps(self.serializer_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_update_valid(self):
        """
        just an update, no insert
        Test update/put
        :return:
        """
        response = self.client.put(
            reverse('neuroglancer-detail', kwargs={'pk': self.urlModel.id}),
            data=json.dumps(self.serializer_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_neuroglancer_url(self):
            response = self.client.get("/neuroglancer")
            request = response.wsgi_request
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_com_url(self):
            response = self.client.get("/center")
            request = response.wsgi_request
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rotations_url(self):
            response = self.client.get("/rotations")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_annotations_url(self):
            response = self.client.get("/rotations")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rotation_url(self):
            response = self.client.get("/rotation/DK52/manual/2")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_annotation_url(self):
            response = self.client.get("/annotation/182/premotor")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
