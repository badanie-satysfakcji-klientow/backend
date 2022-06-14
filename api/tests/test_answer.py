from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Creator, Survey, Item, Option, Interviewee, Submission, Question, Answer
from lorem_text import lorem

# TODO: Test different types of items


class AnswerAPITest(APITestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            email='creator@test.com',
            password='12345678'
        )

        self.interviewee = Interviewee.objects.create(
            email='interviewee@test.com',
            first_name='John',
            last_name='Doe',
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

        self.item = Item.objects.create(
            type=8,
            required=True,
            survey_id=self.survey.id,
        )

        self.question = Question.objects.create(
            order=1,
            value=lorem.words(5),
            item_id=self.item.id,
        )

        self.question2 = Question.objects.create(
            order=2,
            value=lorem.words(5),
            item_id=self.item.id,
        )

        self.option = Option.objects.create(
            content=lorem.words(5),
            item_id=self.item.id,
        )

        self.submission = Submission.objects.create(
            interviewee=self.interviewee,
            survey=self.survey,
        )

        self.answer_data = {
            'submission': self.submission.id,
            'question': self.question.id,
            'content_character': lorem.words(5),
        }

# TODO: Make that work

    def test_can_create_answer(self):
        url = reverse('questions-answer', kwargs={'question_id': self.question.id})
        # TODO: Resolve that conflict
        response = self.client.post(url, self.answer_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Answer.objects.count(), 1)

    def test_can_get_answers_count(self):
        url = reverse('submissions-get-count', kwargs={'survey_id': self.survey.id})

        for i in range(0, 10):
            Answer.objects.create(
                submission=self.submission,
                question=self.question,
                content_character=lorem.words(5),
            )

        for i in range(0, 5):
            Answer.objects.create(
                submission=self.submission,
                question=self.question2,
                content_character=lorem.words(5),
            )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.json()['answers_count']
        self.assertEqual(len(response.json()['answers_count']), 2)
        for i in content:
            self.assertEqual(i['count'], Answer.objects.filter(question=i['id']).count())
