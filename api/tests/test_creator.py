from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.tests.predefined_objects import Predefined
from lorem_text import lorem
from api.models import Creator


class CreatorAPITest(APITestCase):
    def setUp(self):
        self.creator = Predefined.create_creator()

        self.creator_data = {
            'email': f'{lorem.words(1)}@{lorem.words(1)}.{lorem.words(1)}',
            'password': lorem.words(1),
            'phone': lorem.words(1)
        }

    def test_can_create_creator(self):
        url = reverse('creator')
        response = self.client.post(url, self.creator_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Creator.objects.count(), 2)
        self.assertEqual(Creator.objects.filter(pk=response.data['id']).count(), 1)
        self.assertEqual(Creator.objects.get(pk=response.data['id']).email, self.creator_data['email'])

    def test_can_update_creator(self):
        url = reverse('creator-uuid', kwargs={'creator_id': self.creator.id})
        response = self.client.patch(url, {'password': 'new content'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Creator.objects.get(id=self.creator.id).password, 'new content')

    def test_can_get_interviewee(self):
        url = reverse('creator-uuid', kwargs={'creator_id': self.creator.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.creator.id))

    def test_can_delete_interviewee(self):
        url = reverse('creator-uuid', kwargs={'creator_id': self.creator.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Creator.objects.count(), 0)
