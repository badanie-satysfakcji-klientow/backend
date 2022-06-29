from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.tests.predefined_objects import Predefined


class XLXSAPITest(APITestCase):
    def setUp(self):
        self.creator = Predefined.create_creator()
        self.survey = Predefined.create_survey(self.creator)
        self.items = Predefined.create_items(self.survey, 2)
        self.interviewee = Predefined.create_interviewee()
        self.submission = Predefined.create_submission(self.survey, self.interviewee)
        for item in self.items:
            Predefined.create_options(item, 5)
        self.item1_questions = Predefined.create_questions(self.items[0], 5)
        self.item2_questions = Predefined.create_questions(self.items[1], 5, 6)
        self.answers = Predefined.create_answers(self.item1_questions[0], self.submission, 5)

    def test_export_survey_raw_xlsx(self):
        url = reverse('results-raw', kwargs={'survey_id': self.survey.id})
        response = self.client.get(url)
        survey_title = self.survey.title[:15].replace('?', '').replace('\\', '').replace('/', '')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response['Content-Disposition'].startswith(f'attachment; filename={survey_title}'))
        self.assertTrue(response['Content-Disposition'].endswith('.xlsx'))

    def test_export_question_chart_answers_xlsx(self):
        url = reverse('question-results-raw', kwargs={'question_id': self.item1_questions[0].id})
        response = self.client.get(url)
        question_val = self.item1_questions[0].value[:15].replace('?', '').replace('\\', '').replace('/', '')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response['Content-Disposition']
                        .startswith(f'attachment; filename={question_val}'))
        self.assertTrue(response['Content-Disposition'].endswith('.xlsx'))
