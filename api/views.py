from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .serializers import SurveySerializer, SurveyInfoSerializer, ItemSerializer, ItemPatchSerializer, \
    QuestionSerializer, OptionSerializer, AnswerSerializer, SubmissionSerializer, SectionSerializer
from .models import Survey, Item, Question, Option, Answer, Submission
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse


class SurveyViewSet(ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    lookup_url_kwarg = 'survey_id'

    def list(self, request, *args, **kwargs):
        surveys = Survey.objects.all()
        serializer = self.get_serializer(surveys, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'status': 'created', 'survey_id': serializer.data.get('id')}, status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=False, methods=['GET'], name='Get surveys by creator')
    def retrieve_brief(self, request, *args, **kwargs):
        surveys = Survey.objects.filter(creator_id=kwargs['creator_id'])
        serializer = SurveyInfoSerializer(surveys, many=True)  # using different serializer for that action
        return Response({'status': 'OK', 'surveys': serializer.data}, status=status.HTTP_200_OK)

    # check if default update works with that kwarg
    def update(self, request, *args, **kwargs):
        """
        # update survey by its id
        """
        partial = kwargs.pop('partial', False)
        instance = Survey.objects.get(id=kwargs['survey_id'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'status': 'updated'}, status=status.HTTP_200_OK)
        return Response({'status': 'not updated, wrong parameters'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        # delete survey by its id
        """
        survey = Survey.objects.get(pk=kwargs['survey_id'])
        try:
            survey.delete()
            return Response({'status': 'Deleted successfully', 'survey_id': kwargs['survey_id']},
                            status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({'status': 'Not deleted', 'survey_id': kwargs['survey_id']},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send(self, request, *args, **kwargs):
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

    @staticmethod
    def questions_ids_dictionary(questions):
        dictionary = {}
        for question in questions:  # type: Question
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
                         'questions_ids': ItemViewSet.questions_ids_dictionary(serializer.context['questions'])},
                        status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        # update item by its id
        """
        partial = kwargs.pop('partial', False)
        instance = Item.objects.get(id=kwargs['item_id'])
        if partial:
            serializer = ItemPatchSerializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({'status': 'updated'}, status=status.HTTP_200_OK)
            return Response({'status': 'not updated, wrong parameters'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        # serializer.context['type'] = request.data.get('type')
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'status': 'updated'}, status=status.HTTP_200_OK)
        return Response({'status': 'not updated, wrong parameters'}, status=status.HTTP_400_BAD_REQUEST)


class SubmissionViewSet(ModelViewSet):
    queryset = Submission.objects.all()
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


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def update(self, request, *args, **kwargs):
        """
        # update question by its id
        """
        partial = kwargs.pop('partial', False)
        instance = Question.objects.get(id=kwargs['question_id'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response({'status': 'not updated, wrong parameters'}, status=status.HTTP_400_BAD_REQUEST)


class OptionViewSet(ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

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
