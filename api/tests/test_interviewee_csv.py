from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from io import BytesIO
from api.models import Interviewee, Creator, Survey
from lorem_text import lorem


class CSVIntervieweeAPITest(APITestCase):
    def setUp(self):
        self.interviewee = Interviewee.objects.create(
            email='i@test.com',
            first_name='Krystian',
            last_name='Tail'
        )

        self.interviewee_data = {
            'email': f'{lorem.words(1)}@{lorem.words(1)}.{lorem.words(1)}',
            'first_name': lorem.words(2),
            'last_name': lorem.words(2)
        }

        self.creator = Creator.objects.create(
            email='cr@test.com',
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

        self.rev_csv_url = reverse('intervieweescsv-list', args=[self.creator.id])

    def test_export_interviewees(self):
        response = self.client.get(self.rev_csv_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="interviewees'))
        self.assertTrue(response['Content-Disposition'].endswith('.csv"'))

    def test_can_import_save_interviewees(self):
        url = f'{self.rev_csv_url}?save=true'
        file = BytesIO(self.client.get(self.rev_csv_url).content)
        response = self.client.post(url, {'file': file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['status'], 'respondents saved')

    def test_can_import_send_interviewees(self):
        url = f'{self.rev_csv_url}?send_survey={self.survey.id}'
        file = BytesIO(self.client.get(self.rev_csv_url).content)
        response = self.client.post(url, {'file': file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'sending process started')

    def test_can_import_save_send_interviewees(self):
        url = f'{self.rev_csv_url}?save=true&send_survey={self.survey.id}'
        file = BytesIO(self.client.get(self.rev_csv_url).content)
        response = self.client.post(url, {'file': file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['status'], 'respondents saved, sending process started')

    def test_can_do_nothing_interviewees(self):
        file = BytesIO(self.client.get(self.rev_csv_url).content)
        response = self.client.post(self.rev_csv_url, {'file': file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['status'], 'error')
