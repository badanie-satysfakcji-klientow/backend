from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Question
from api.tests.predefined_objects import Predefined


class QuestionAPITest(APITestCase):
    def setUp(self):
        self.creator = Predefined.create_creator()
        self.survey = Predefined.create_survey(self.creator)
        self.items = Predefined.create_items(self.survey, 2)
        for item in self.items:
            Predefined.create_options(item, 5)

        self.item1_questions = Predefined.create_questions(self.items[0], 5)
        self.item2_questions = Predefined.create_questions(self.items[1], 5, 6)

    # create endpoint for creating questions
    # def test_can_create_question(self):
    #    url = reverse('questions-answer', kwargs={'question_id': self.item.id})
    def test_can_update_question(self):
        url = reverse('questions-uuid', kwargs={'question_id': self.item1_questions[0].id})
        response = self.client.patch(url, {'value': 'new value'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Question.objects.get(id=self.item1_questions[0].id).value, 'new value')

    def test_can_delete_question(self):
        # removing 3
        # before: 1, 2, 3, 4, 5
        # after: 1, 2, X, 3, 4
        url = reverse('questions-uuid', kwargs={'question_id': self.item1_questions[2].id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=self.item1_questions[2].id).exists())
        self.item1_questions.pop(2)
        for i in range(len(self.item1_questions)):
            self.assertEquals(Question.objects.get(id=self.item1_questions[i].id).order, i + 1)

    def test_can_change_questions_order_backwards(self):
        # change 4 to 2
        # before: 1, 2, 3, 4, 5
        after = [1, 3, 4, 2, 5]
        url = reverse('questions-uuid', kwargs={'question_id': self.item1_questions[3].id})
        response = self.client.patch(url, {'order': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(len(self.item1_questions)):
            self.assertEqual(Question.objects.get(id=self.item1_questions[i].id).order, after[i])

    def test_can_change_questions_order_forwards(self):
        # change 2 to 4
        # before: 1, 2, 3, 4, 5
        after = [1, 4, 2, 3, 5]
        url = reverse('questions-uuid', kwargs={'question_id': self.item1_questions[1].id})
        response = self.client.patch(url, {'order': 4})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(len(self.item1_questions)):
            self.assertEqual(Question.objects.get(id=self.item1_questions[i].id).order, after[i])

    def test_can_not_change_order_to_negative_number(self):
        # change 4 to -1 should fail
        url = reverse('questions-uuid', kwargs={'question_id': self.item1_questions[3].id})
        response = self.client.patch(url, {'order': -1})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Question.objects.get(id=self.item1_questions[3].id).order, 4)

    def test_can_not_change_questions_order_to_others_item_range(self):
        # change 4 to 6 should fail
        url = reverse('questions-uuid', kwargs={'question_id': self.item1_questions[3].id})
        response = self.client.patch(url, {'order': 6})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Question.objects.get(id=self.item1_questions[3].id).order, 4)
