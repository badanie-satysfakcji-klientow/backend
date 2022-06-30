from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey, Interviewee, Submission
from lorem_text import lorem


class SubmissionAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
        )

        self.interviewee = Interviewee.objects.create(
            email='interviewee@test.com',
            first_name='John',
            last_name='Doe',
        )

        self.survey = Survey.objects.create(**{
            'title': lorem.words(5),
            'description': lorem.sentence(),
            'creator_id': self.creator,
            'starts_at': '2022-06-02T04:20:00Z',
            'expires_at': '2023-06-22T02:26:22Z',
            'paused': False,
            'anonymous': False,
            'greeting': 'Hi there!',
            'farewell': lorem.words(2)
        })

        self.submission_data = {
            'interviewee': self.interviewee.id,
        }

    def test_can_create_submission(self):
        url = reverse('submit-list', kwargs={'survey_id': self.survey.id})
        response = self.client.post(url, self.submission_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)
