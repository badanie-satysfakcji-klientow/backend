from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey
# needs lorem-text package
# pip install lorem-text
from lorem_text import lorem

# TODO: Create tests for:
#   - send survey via mail
#   - get survey brief info


class GetSurveyAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
        )

        self.survey_data = {
            'title': lorem.words(5),
            'description': lorem.sentence(),
            'creator_id': self.creator,
            'starts_at': '2022-06-02T04:20:00Z',
            'expires_at': '2023-06-22T02:26:22Z',
            'paused': False,
            'anonymous': False,
            'greeting': 'Hi there!',
            'farewell': lorem.words(2)
        }

    def test_can_get_survey(self):
        survey = Survey.objects.create(**self.survey_data)
        url = reverse('surveys-uuid', kwargs={'survey_id': survey.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], survey.title)


class DeleteSurveyAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
        )

        self.survey_data = {
            'title': lorem.words(5),
            'description': lorem.sentence(),
            'creator_id': self.creator,
            'starts_at': '2022-06-02T04:20:00Z',
            'expires_at': '2023-06-22T02:26:22Z',
            'paused': False,
            'anonymous': False,
            'greeting': 'Hi there!',
            'farewell': lorem.words(2)
        }

    def test_can_delete_survey(self):
        survey = Survey.objects.create(**self.survey_data)

        url = reverse('surveys-uuid', kwargs={'survey_id': survey.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Survey.objects.count(), 0)


class CreateSurveyAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
        )

        self.survey_data = {
            'title': lorem.words(5),
            'description': lorem.sentence(),
            'creator_id': self.creator.id,
            'starts_at': '2022-06-02T04:20:00Z',
            'expires_at': '2023-06-22T02:26:22Z',
            'paused': False,
            'anonymous': False,
            'greeting': 'Hi there!',
            'farewell': lorem.words(2)
        }

    def test_can_create_survey(self):
        url = reverse('surveys')
        response = self.client.post(url, self.survey_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 1)
        self.assertEqual(Survey.objects.first().title, self.survey_data['title'])


class UpdateSurveyAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
        )

        self.new_creator = Creator.objects.create(
            email='new_creator@test.com',
            password='87654321'
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

    def test_can_update_survey(self):
        url = reverse('surveys-uuid', kwargs={'survey_id': self.survey.id})
        response = self.client.patch(url, {'title': 'New title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.survey.title, 'New title')

    def test_can_pause_survey(self):
        url = reverse('surveys-uuid', kwargs={'survey_id': self.survey.id})
        response = self.client.patch(url, {'paused': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.survey.paused, True)

    def test_can_change_survey_creator(self):
        url = reverse('surveys-uuid', kwargs={'survey_id': self.survey.id})
        response = self.client.patch(url, {'creator_id': self.new_creator.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.survey.creator_id.id, self.creator.id)


class ShowSurveyBriefInfoAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
        )

        for i in range(5):
            survey_data = {
                'title': lorem.words(5),
                'description': lorem.sentence(),
                'creator_id': self.creator,
                'starts_at': '2022-06-02T04:20:00Z',
                'expires_at': '2023-06-22T02:26:22Z',
                'paused': False,
                'anonymous': False,
                'greeting': 'Hi there!',
                'farewell': lorem.words(2)
            }
            Survey.objects.create(**survey_data)

    def test_can_get_survey_brief_info(self):
        url = reverse('surveys-brief-info', kwargs={'creator_id': self.creator.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['surveys']), 5)


class SendSurveyAPITest(APITestCase):
    def setUp(self):
        # some setup
        pass

    def test_can_send_survey(self):
        # some test
        self.assertTrue(False)
