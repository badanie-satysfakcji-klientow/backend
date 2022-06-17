from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .serializers import SurveySerializer, SurveyInfoSerializer, ItemSerializer, \
    QuestionSerializer, OptionSerializer, AnswerSerializer, SubmissionSerializer, SectionSerializer, \
    AnswerQuestionCountSerializer
from .models import Survey, Item, Question, Option, Answer, Submission, Section, Interviewee
from django.core.mail import send_mass_mail
from django.core.mail import get_connection, EmailMultiAlternatives
from threading import Thread
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
            serializer.is_valid(raise_exception=True)       # or just if
        except serializers.ValidationError as e:
            return Response({'status': 'error', 'message': e.args},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response({'status': 'success', 'answer_id': serializer.data.get('id')}, status=status.HTTP_201_CREATED)


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


class SendEmailViewSet(ModelViewSet):
    queryset = Interviewee.objects.all()

    @action(detail=False, methods=['POST'])
    def send(self, request, *args, **kwargs):
        """
        send a mail with link to survey
        eg. http://127.0.0.1:4200/survey/survey_uuid
        """
        survey_id = kwargs['survey_id']
        try:
            interviewees = request.data['interviewees']
        except KeyError as e:
            hint = "Provide correct interviewee id list eg.  " \
                   "{'interviewees': ['7d01d6b3-df2a-42fc-ab9e-ffe5f39a9685', '8e813c93-37a7-429f-926c-0ac092b30c79']}"
            return Response(
                {'status': 'error', 'message': e.args, 'hint': hint}, status=status.HTTP_400_BAD_REQUEST)

        try:
            selected_interviewees_emails = \
                [self.queryset.get(id=interviewee_id).email for interviewee_id in interviewees]
            send_my_mass_mail(survey_id, selected_interviewees_emails)
        except Exception as e:
            return Response({'survey_id': survey_id, 'status': 'error', 'message': e.args},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'survey_id': survey_id, 'status': 'sending process started'}, status=status.HTTP_200_OK)


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)


def send_my_mass_mail(survey_id, email_list, html=True) -> None:
    """
    starts new thread sending mass email (to prevent API freeze) - significantly speeds up the request
    current link to survey: http://127.0.0.1:4200/survey/<survey_id>
    """
    survey = Survey.objects.get(pk=survey_id)
    survey_title = survey.title
    partial_link = reverse('surveys-uuid', args=[survey_id]).removeprefix('/api').replace('surveys', 'survey')
    survey_link = settings.DOMAIN_NAME + partial_link

    context = {'link': survey_link}
    html_message = render_to_string('email_template.html', context=context)
    txt_message = strip_tags(html_message)

    if html:
        data_tuple_html = ((survey_title, txt_message, html_message, None, email_list),)
        t = Thread(target=send_mass_html_mail, args=(data_tuple_html,))
        t.start()
    else:
        data_tuple_txt = ((survey_title, txt_message, None, email_list),)
        t = Thread(target=send_mass_mail, args=(data_tuple_txt,))
        t.start()


