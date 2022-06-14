from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .serializers import SurveySerializer, SurveyInfoSerializer, ItemSerializer, \
    QuestionSerializer, OptionSerializer, AnswerSerializer, SubmissionSerializer, SectionSerializer, \
    AnswerQuestionCountSerializer, SurveyResultSerializer
from .models import Survey, Item, Question, Option, Answer, Submission, Section
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse


class SurveyViewSet(ModelViewSet):
    queryset = Survey.objects.prefetch_related('items')
    serializer_class = SurveySerializer
    lookup_url_kwarg = 'survey_id'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'status': 'created', 'survey_id': serializer.data.get('id')}, status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=False, methods=['GET'], name='Get surveys by creator')
    def retrieve_brief(self, request, *args, **kwargs):         # use prefetch_related
        surveys = Survey.objects.filter(creator_id=kwargs['creator_id'])
        serializer = SurveyInfoSerializer(surveys, many=True)  # using different serializer for that action
        return Response({'status': 'OK', 'surveys': serializer.data}, status=status.HTTP_200_OK)

    def send(self, request, *args, **kwargs):       # send_mail -> send_mass_mail
        """
        send a mail with link to survey
        """
        survey_id = kwargs['survey_id']
        survey = Survey.objects.get(pk=survey_id)
        survey_title = survey.title
        # http://127.0.0.1:4200/surveys/uuid
        survey_link = settings.DOMAIN_NAME + reverse('surveys-uuid', args=[survey_id]).removeprefix('/api')
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
            return Response({'status': 'Sent successfully', 'survey_id': kwargs['survey_id']},
                            status=status.HTTP_200_OK)
        except Exception as e:   # chwilowo zeby bylo jakiekolwiek zabezpieczenie, w przyszlosci mozna rozwinac
            return Response({'status': 'Not sent', 'survey_id': survey_id, 'message': e.args},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_url_kwarg = 'item_id'

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
                         'questions_ids': serializer.context['questions']},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):     # unnecessary
        """
        # update item by its id
        """
        partial = kwargs.pop('partial', False)
        instance = Item.objects.get(id=kwargs['item_id'])
        if partial:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.context['type'] = request.data.get('type')
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({'status': 'updated'}, status=status.HTTP_200_OK)
            return Response({'status': 'not updated, wrong parameters'}, status=status.HTTP_400_BAD_REQUEST)


class AnswersCountViewSet(ModelViewSet):
    serializer_class = AnswerQuestionCountSerializer

    def get_queryset(self):
        submission_queryset = Submission.objects.filter(survey=self.kwargs['survey_id'])
        questions_list = Answer.objects.filter(submission__in=submission_queryset).values_list('question', flat=True)
        return Question.objects.filter(id__in=questions_list)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        try:
            return Response({'status': 'OK', 'answers_count': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'Not found', 'message': e.args}, status=status.HTTP_404_NOT_FOUND)
        pass


class SubmissionViewSet(ModelViewSet):
    serializer_class = SubmissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context['survey_id'] = kwargs.get('survey_id')
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({'status': 'error', 'message': e.detail['non_field_errors'][0]},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response({'status': 'success', 'submission_id': serializer.data.get('id')},
                        status=status.HTTP_201_CREATED)


class AnswerViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context['question_id'] = kwargs.get('question_id')
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({'status': 'success', 'answer_id': serializer.data.get('id')},
                            status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'status': 'error', 'message': e.args},
                            status=status.HTTP_400_BAD_REQUEST)


class SectionViewSet(ModelViewSet):
    serializer_class = SectionSerializer
    queryset = Section.objects.all()

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


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    lookup_url_kwarg = 'question_id'


class OptionViewSet(ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

    lookup_url_kwarg = 'option_id'

    def update(self, request, *args, **kwargs):
        """
        # update option by its id
        """
        partial = kwargs.pop('partial', False)
        instance = Option.objects.get(id=kwargs['option_id'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response({'status': 'not updated, wrong parameters'}, status=status.HTTP_400_BAD_REQUEST)


class SurveyResultViewSet(ModelViewSet):
    serializer_class = SurveyResultSerializer
    queryset = Question.objects.all()

    def retrieve(self, request, *args, **kwargs):
        survey = self.get_queryset().get(id=kwargs['question_id'])
        serializer = SurveyResultSerializer(survey)
        try:
            return Response({'status': 'OK', 'question_results': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': e.args}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        # get result by survey id
        """
        # get all question results for a survey
        result_info_serializer = self.get_serializer(self.get_queryset().get(id=self.kwargs['survey_id']), many=False)
        result_serializer = SurveyResultSerializer(Question.objects.filter(survey=kwargs['survey_id']), many=True)
        try:
            return Response({'status': 'OK',
                             'results_info': result_info_serializer.data,
                             'results': result_serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': e.args}, status=status.HTTP_400_BAD_REQUEST)
