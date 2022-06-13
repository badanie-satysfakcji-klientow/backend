from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey, Item
from lorem_text import lorem

# TODO: Create tests for:
#   - updating item id (not allowed)
#   - updating survey_id (not allowed)


class ItemAPITest(APITestCase):
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

        self.item_data = {
            'type': 1,
            'required': True,
            'survey_id': self.survey.id,
        }

    def test_can_create_item(self):
        url = reverse('survey-items', kwargs={'survey_id': self.survey.id})
        response = self.client.post(url, self.item_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 1)

    def test_can_update_item(self):
        item = Item.objects.create(
            type=1,
            required=True,
            survey_id=self.survey.id,
        )
        url = reverse('items-uuid', kwargs={'item_id': item.id})
        # TODO: Resolve that conflict
        response = self.client.patch(url, {'type': 2, 'required': False})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Item.objects.get().type, 2)

    def test_can_delete_item(self):
        item = Item.objects.create(
            type=1,
            required=True,
            survey_id=self.survey.id,
        )
        url = reverse('items-uuid', kwargs={'item_id': item.id})
        response = self.client.delete(url, {'id': item.id})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Item.objects.count(), 0)
