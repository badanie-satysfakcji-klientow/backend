from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Interviewee, Survey, Creator
from lorem_text import lorem


class EmailAPITest(APITestCase):
    def setUp(self):
        self.interviewee = Interviewee.objects.create(
            email='i1@test.test',
            first_name='t_email',
            last_name='last'
        )

        self.new_interviewee = Interviewee.objects.create(
            email='interviewetest@test.test',
            first_name='test_email',
            last_name='test'
        )

        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
        )

        self.survey = Survey.objects.create(
            title=lorem.words(5),
            description=lorem.sentence(),
            creator_id=self.creator,
            starts_at='2022-06-02T04:20:00Z',
            expires_at='2023-06-22T02:26:22Z',
            paused=False,
            anonymous=False,
            greeting='Hi there!',
            farewell=lorem.words(2)
        )

        self.interviewee_ids = [self.new_interviewee.id, self.interviewee.id]
        self.email_list = [f'{lorem.words(1)}@{lorem.words(1)}.{lorem.words(1)}',
                           f'{lorem.words(1)}@{lorem.words(1)}.{lorem.words(1)}',
                           f'{lorem.words(1)}@{lorem.words(1)}.{lorem.words(1)}']

    def test_can_send_survey_selected(self):
        url = f'{reverse("send-manually", kwargs={"survey_id": self.survey.id})}?selected=true'
        response = self.client.post(url, {'interviewees': self.interviewee_ids})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['survey_id'], str(self.survey.id))
        self.assertEqual(response.json()['status'], 'sending process started')

    def test_can_send_survey_email_list(self):
        url = reverse('send-manually', kwargs={'survey_id': self.survey.id})
        response = self.client.post(url, {'interviewees': self.email_list})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['survey_id'], str(self.survey.id))
        self.assertEqual(response.json()['status'], 'sending process started')
