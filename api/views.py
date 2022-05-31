from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import SurveySerializer, ItemSerializer, AnswerSerializer, SubmissionSerializer, SectionSerializer
from .models import Survey, Item, Question, Answer, Submission
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse


class SurveyViewSet(ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def list(self, request, *args, **kwargs):
        surveys = Survey.objects.all()
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'status': 'created', 'survey_id': serializer.data.get('id')}, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """
        get survey by its id
        """
        survey = Survey.objects.get(pk=kwargs.get('survey_id'))
        serializer = SurveySerializer(survey)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        # update survey by its id
        """
        pass

    def partial_update(self, request, *args, **kwargs):
        """
        # update survey by its id
        """

    def destroy(self, request, *args, **kwargs):
        """
        # delete survey by its id
        """
        survey = Survey.objects.get(pk=kwargs['survey_id'])
        try:
            survey.delete()
            return Response({'status': 'Deleted successfully', 'survey_id': kwargs['survey_id']}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({'status': 'Not deleted', 'survey_id': kwargs['survey_id']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send(self, request, *args, **kwargs):
        """
        send a mail with link to survey
        """
        survey_id = kwargs['survey_id']
        survey = Survey.objects.get(pk=survey_id)
        survey_title = survey.title
        survey_link = settings.DOMAIN_NAME + reverse('surveys-uuid', args=[survey_id]).removeprefix('/api')   # http://127.0.0.1:4200/surveys/uuid
        recipient_list = request.data['recipient_list']

        context = {'link': survey_link}
        html_message = render_to_string('email_template.html', context=context)
        message = strip_tags(html_message)

        try:
            send_mail(subject=survey_title,
                      message=message,
                      from_email=None,
                      recipient_list=recipient_list,
                      html_message=html_message,
                      fail_silently=False)
            return Response({'status': 'Sent successfully', 'survey_id': kwargs['survey_id']}, status=status.HTTP_200_OK)
        except Exception:   # chwilowo zeby bylo jakiekolwiek zabezpieczenie, w przyszlosci mozna rozwinac
            return Response({'status': 'Not sent', 'survey_id': survey_id}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def questions_ids_dictionary(self, questions):
        dictionary = {}
        for question in questions: # type: Question
            dictionary[question.order] = question.id
        return dictionary

    def create(self, request, *args, **kwargs) -> Response:
        """
        # save survey question by its id
        """
        serializer = self.get_serializer(data=request.data)
        serializer.context['survey_id'] = kwargs.get('survey_id')
        serializer.context['type'] = request.data.get('type')
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        return Response({'status': 'created item',
                         'item_id': serializer.data.get('id'),
                         'questions_ids': self.questions_ids_dictionary(serializer.context['questions'])},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        # update survey question by its id
        """
        pass

    def partial_update(self, request, *args, **kwargs):
        """
        # update survey question by its id
        """
        
        
class SubmissionViewSet(ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context['survey_id'] = kwargs.get('survey_id')
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({'status': 'error', 'message': e.detail['non_field_errors'][0]}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response({'status': 'success', 'submission_id': serializer.data.get('id')}, status=status.HTTP_201_CREATED)


class AnswerViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context['question_id'] = kwargs.get('question_id')
        self.perform_create(serializer)
        return Response({'status': 'success', 'answer_id': serializer.data.get('id')}, status=status.HTTP_201_CREATED)


class SectionViewSet(ModelViewSet):
    serializer_class = SectionSerializer

    def list(self, request, *args, **kwargs):
        pass

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.context['survey_id'] = kwargs.get('survey_id')
        # validate data
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({'status': 'error', 'message': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'status': 'created section',
                         'section_id': serializer.data.get('id')},
                        status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        pass
