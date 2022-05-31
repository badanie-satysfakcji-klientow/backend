from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import SurveySerializer, ItemSerializer
from .models import Survey, Item, Question
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
        pass

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
        survey.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def send(self, request, *args, **kwargs):
        """
        send a mail with link to survey
        """
        survey_id = kwargs['survey_id']
        survey = Survey.objects.get(pk=survey_id)
        survey_title = survey.title
        survey_link = settings.DOMAIN_NAME + reverse('surveys', args=[survey_id])   # http://127.0.0.1:4200/api/surveys/uuid
        recipient_list = request.data['recipient_list']
        print(survey_link)
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
