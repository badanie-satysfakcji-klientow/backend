from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Interviewee
from lorem_text import lorem


class IntervieweeAPITest(APITestCase):
    def setUp(self):
        self.interviewee = Interviewee.objects.create(
            email='interviewee@test.com',
            first_name='Krystian',
            last_name='Tail'
        )

        self.interviewee_data = {
            'email': f'{lorem.words(1)}@{lorem.words(1)}.{lorem.words(1)}',
            'first_name': lorem.words(2),
            'last_name': lorem.words(2)
        }

    def test_can_create_interviewee(self):
        url = reverse('interviewee')
        response = self.client.post(url, self.interviewee_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Interviewee.objects.count(), 2)
        self.assertEqual(Interviewee.objects.filter(pk=response.data['id']).count(), 1)
        self.assertEqual(Interviewee.objects.get(pk=response.data['id']).email, self.interviewee_data['email'])

    def test_can_update_interviewee(self):
        url = reverse('interviewee-uuid', kwargs={'interviewee_id': self.interviewee.id})
        response = self.client.patch(url, {'first_name': 'new content'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Interviewee.objects.get(id=self.interviewee.id).first_name, 'new content')

    def test_can_get_interviewee(self):
        url = reverse('interviewee-uuid', kwargs={'interviewee_id': self.interviewee.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.interviewee.id))

    def test_can_get_interviewee_list(self):
        for i in range(6):
            Interviewee.objects.create(**self.interviewee_data)

        url = reverse('interviewee')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)

    def test_can_delete_interviewee(self):
        url = reverse('interviewee-uuid', kwargs={'interviewee_id': self.interviewee.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Interviewee.objects.count(), 0)
