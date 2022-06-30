from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey, SurveySent, Submission
from lorem_text import lorem


class ResponseRateAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='test@mail.com',
            password='12345678'
        )
        self.survey = Survey.objects.create(
            creator_id=self.creator,
            title=lorem.words(5),
            paused=False,
            anonymous=True,
        )

    # sent = 2, answered = 1
    def test_can_get_response_rate_2_1(self):
        survey_sent = SurveySent.objects.create(**{'survey_id': self.survey.id, 'email': 'test1@mail.com'})
        SurveySent.objects.create(**{'survey_id': self.survey.id, 'email': 'test2@mail.com'})

        Submission.objects.create(
            survey_id=self.survey.id,
            hash_id=survey_sent.id
        )

        url = reverse('surveys-brief-info', args=[self.creator.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['results'][0]['response_rate'],
                         {'sent': 2, 'submitted': 1, 'response_rate': 50.0})

    def test_can_get_response_rate_1_0(self):
        SurveySent.objects.create(**{'survey_id': self.survey.id, 'email': 'test1@mail.com'})

        url = reverse('surveys-brief-info', args=[self.creator.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['response_rate'],
                         {'sent': 1, 'submitted': 0, 'response_rate': 0.0})

    def test_can_get_response_rate_0_0(self):
        url = reverse('surveys-brief-info', args=[self.creator.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['response_rate'],
                         {'sent': 0, 'submitted': 0, 'response_rate': 0})
