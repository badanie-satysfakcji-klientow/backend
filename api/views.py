from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import SurveySerializer, ItemSerializer
from .models import Survey, Item, Question


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

