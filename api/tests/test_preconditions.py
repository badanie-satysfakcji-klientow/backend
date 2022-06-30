from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey, Item, Question, Precondition, Option
from lorem_text import lorem


class SectionAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
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

        self.survey_item1 = Item.objects.create(
            type=10,
            required=True,
            survey_id=self.survey.id,
        )

        Question.objects.create(
            order=1,
            value=lorem.words(3),
            item_id=self.survey_item1.id,
        )

        self.item1_option1 = Option.objects.create(
            content=lorem.words(3),
            item=self.survey_item1
        )

        self.item1_option2 = Option.objects.create(
            content=lorem.words(3),
            item=self.survey_item1
        )

        self.survey_item2 = Item.objects.create(
            type=1,
            required=True,
            survey_id=self.survey.id,
        )

        self.survey_item3 = Item.objects.create(
            type=2,
            required=True,
            survey_id=self.survey.id,
        )

        Question.objects.create(
            order=2,
            value=lorem.words(3),
            item_id=self.survey_item2.id,
        )

        Question.objects.create(
            order=3,
            value=lorem.words(3),
            item_id=self.survey_item3.id,
        )

        self.item_precondition_data = {
            'expected_option': self.item1_option1.id,
            'next_item': self.survey_item3.id
        }

        self.item_precondition = Precondition.objects.create(
            expected_option=self.item1_option1,
            item=self.survey_item1,
            next_item=self.survey_item2
        )

    def test_can_create_precondition(self):
        url = reverse('precondition-list', args=[self.survey.id])
        response = self.client.post(url, self.item_precondition_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Precondition.objects.count(), 2)  # 1 existing, 1 created

    def test_can_get_precondition(self):
        url = reverse('precondition-list', args=[self.survey.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_can_update_precondition(self):
        url = reverse('precondition-detail', args=[self.survey.id, self.item_precondition.id])

        response = self.client.patch(url, {'expected_option': self.item1_option2.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Precondition.objects.get(id=self.item_precondition.id).expected_option, self.item1_option2)

    def test_can_delete_precondition(self):
        url = reverse('precondition-detail', args=[self.survey.id, self.item_precondition.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Precondition.objects.count(), 0)
