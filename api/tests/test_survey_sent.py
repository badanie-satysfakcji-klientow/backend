from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey, SurveySent
from lorem_text import lorem


class SurveySentAPITest(APITestCase):
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

        self.survey_sent_data = {
            'survey_id': self.survey.id,
            'email': 'some_int@mail.com'
        }

    def test_can_send_anonymous_survey_via_mail(self):
        SurveySent.objects.create(**self.survey_sent_data)

        self.assertEqual(SurveySent.objects.count(), 1)

    def test_can_get_sections_anonymously(self):
        survey_sent = SurveySent.objects.create(**self.survey_sent_data)

        url = reverse('sections-anonymous', args=[survey_sent.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_get_survey_anonymously(self):
        survey_sent = SurveySent.objects.create(**self.survey_sent_data)

        url = reverse('surveys-anonymous', kwargs={'survey_hash': survey_sent.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_create_submission_anonymously(self):
        survey_sent = SurveySent.objects.create(**self.survey_sent_data)

        url = reverse('submit-anonymous', kwargs={'survey_hash': survey_sent.id})
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
