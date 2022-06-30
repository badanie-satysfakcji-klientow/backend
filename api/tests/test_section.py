from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey, Item, Section, Question
# needs lorem-text package
# pip install lorem-text
from lorem_text import lorem

# TODO: Create tests for:
#   - update section start_item_id
#   - update section end_item_id


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
            type=1,
            required=True,
            survey_id=self.survey.id,
        )
        self.item1_question = Question.objects.create(
            order=1,
            value=lorem.words(3),
            item_id=self.survey_item1.id,
        )
        self.survey_item2 = Item.objects.create(
            type=2,
            required=True,
            survey_id=self.survey.id,
        )
        self.item2_question = Question.objects.create(
            order=2,
            value=lorem.words(3),
            item_id=self.survey_item2.id,
        )
        self.survey_item3 = Item.objects.create(
            type=2,
            required=True,
            survey_id=self.survey.id,
        )
        self.item3_question = Question.objects.create(
            order=3,
            value=lorem.words(3),
            item_id=self.survey_item3.id,
        )

        self.section_data = {
            'start_item': self.survey_item1.id,
            'end_item': self.survey_item2.id,
            'title': lorem.words(5),
            'description': lorem.sentence(),
        }

    def test_can_create_section(self):
        url = reverse('section-list', kwargs={'survey_id': self.survey.id})
        response = self.client.post(url, self.section_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Section.objects.count(), 1)

    # TODO: Create functionality- delete section
    # def test_delete_section(self):
    #     section = Section.objects.create(
    #         start_item=self.survey_item1,
    #         end_item=self.survey_item2,
    #         title=lorem.words(5),
    #         description=lorem.sentence(),
    #     )
    #     url = reverse('sections-uuid', kwargs={'section_id': section.id})
    #     response = self.client.delete(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(Section.objects.count(), 0)

    def test_can_create_separate_sections(self):
        url = reverse('section-list', kwargs={'survey_id': self.survey.id})

        # according to issue #74 we make 3 requests
        # same url
        response = self.client.post(url, {
            'start_item': self.survey_item1.id,
            'end_item': self.survey_item1.id,
            'title': lorem.words(5),
            'description': lorem.sentence(),
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Section.objects.count(), 1)

        response = self.client.post(url, {
            'start_item': self.survey_item2.id,
            'end_item': self.survey_item2.id,
            'title': lorem.words(5),
            'description': lorem.sentence(),
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Section.objects.count(), 2)

        response = self.client.post(url, {
            'start_item': self.survey_item3.id,
            'end_item': self.survey_item3.id,
            'title': lorem.words(5),
            'description': lorem.sentence(),
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Section.objects.count(), 3)

    def test_can_not_create_section_without_question(self):
        # create item without question
        no_question_item = Item.objects.create(
            type=1,
            required=True,
            survey_id=self.survey.id,
        )

        url = reverse('section-list', kwargs={'survey_id': self.survey.id})
        response = self.client.post(url, {
            'start_item': no_question_item.id,
            'end_item': no_question_item.id,
            'title': lorem.words(5),
            'description': lorem.sentence(),
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Section.objects.count(), 0)
