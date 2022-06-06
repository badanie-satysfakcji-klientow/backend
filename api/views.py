from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import SurveySerializer, ItemSerializer, ItemPatchSerializer, QuestionSerializer, OptionSerializer
from .models import Survey, Item, Question, Option


class SurveyViewSet(ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    lookup_field = 'survey_id'

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