import json
from rest_framework import status
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
# Create your tests here.
from brain.models import Animal
from neuroglancer.models import UrlModel
from neuroglancer.serializers import UrlSerializer

# initialize the APIClient app
from neuroglancer.views import UrlViewSet

client = Client()



class TestUrlModel(TransactionTestCase):

    def setUp(self):
        super_user = User.objects.create_superuser(username='super', email='super@email.org',
                                                   password='pass')
        # ids 168, 188,210,211,209,200
        id = 164
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

    def test_create_valid(self):
        """
        1st insert
        test inserting good data
        :return:
        """
        response = client.post(
            reverse('neuroglancer-list'),
            data=json.dumps(self.serializer_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid(self):
        """
        should be a failed insert
        test inserting bad data
        :return:
        """
        response = client.post(
            reverse('neuroglancer-list'),
            data=json.dumps(self.bad_serializer_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_update_valid(self):
        """
        just an update, no insert
        Test update/put
        :return:
        """
        response = client.put(
            reverse('neuroglancer-detail', kwargs={'pk': self.urlModel.id}),
            data=json.dumps(self.serializer_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
