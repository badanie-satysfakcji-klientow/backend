from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey, Item, Option
from lorem_text import lorem


class OptionAPITest(APITestCase):
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

        self.item = Item.objects.create(
            type=1,
            required=True,
            survey_id=self.survey.id,
        )

        self.option = Option.objects.create(
            content=lorem.words(5),
            item_id=self.item.id,
        )

    def test_can_update_option(self):
        url = reverse('options-uuid', kwargs={'option_id': self.option.id})
        response = self.client.patch(url, {'content': 'new content'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Option.objects.get(id=self.option.id).content, 'new content')
