from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import SurveySerializer, ItemSerializer
from .models import Survey, Item
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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

    def send(self, request, *args, **kwargs):
        """
        send a mail with link to survey
        """
        survey_title = request.data['survey_title']
        survey_link = request.data['survey_link']
        recipient_list = request.data['recipient_list']

        context = {'link': survey_link}
        html_message = render_to_string('email_template.html', context=context)
        message = strip_tags(html_message)

        send_mail(subject=survey_title,
                  message=message,
                  from_email=None,
                  recipient_list=recipient_list,
                  html_message=html_message,
                  fail_silently=False)

        return Response(status=status.HTTP_200_OK)


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def create(self, request, *args, **kwargs) -> Response:
        """
        # save survey question by its id
        """
        serializer = self.get_serializer(data=request.data)
        serializer.context['survey_id'] = kwargs.get('survey_id')
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'status': 'created item'}, status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        """
        # update survey question by its id
        """
        pass

    def partial_update(self, request, *args, **kwargs):
        """
        # update survey question by its id
        """