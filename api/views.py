import datetime
from django.db.models import F
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .serializers import SurveySerializer, SurveyInfoSerializer, ItemSerializer, \
    QuestionSerializer, OptionSerializer, AnswerSerializer, SubmissionSerializer, SectionSerializer, \
    AnswerQuestionCountSerializer, SurveyResultSerializer, SurveyResultInfoSerializer, \
    IntervieweeSerializer, IntervieweeUploadSerializer, SurveyResultFullSerializer, PreconditionSerializer
from .models import Survey, Item, Question, Option, Answer, Submission, Section, Interviewee, Precondition
from django.http import HttpResponse
import pandas as pd
import csv
from api.utils import send_my_mass_mail, xlsx_question_charts_file, xlsx_survey_results
# from api.utils import xlsx_survey_results2


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

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except AttributeError as e:
            return Response({'status': 'error', 'message': e.args})

    @action(detail=False, methods=['GET'], name='Get surveys by creator')
    def retrieve_brief(self, request, *args, **kwargs):  # use prefetch_related
        surveys = Survey.objects.prefetch_related('items', 'items__questions').filter(creator_id=kwargs['creator_id'])
        serializer = SurveyInfoSerializer(surveys, many=True)  # using different serializer for that action
        return Response({'status': 'OK', 'surveys': serializer.data}, status=status.HTTP_200_OK)


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_url_kwarg = 'item_id'

    # TODO: override get_serializer_context

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
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):  # unnecessary
        """
        # update item by its id
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.context['type'] = request.data.get('type')
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data, status=status.HTTP_200_OK)


class AnswersCountViewSet(ModelViewSet):
    serializer_class = AnswerQuestionCountSerializer

    def get_queryset(self):
        submission_queryset = Submission.objects.filter(survey=self.kwargs['survey_id'])
        answers_query = Answer.objects \
            .select_related('question') \
            .filter(submission__in=submission_queryset).values_list('question_id', flat=True)
        return Question.objects.filter(id__in=answers_query)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        try:
            return Response({'status': 'OK', 'answers_count': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'Not found', 'message': e.args}, status=status.HTTP_404_NOT_FOUND)
        pass


class SubmissionViewSet(ModelViewSet):
    serializer_class = SubmissionSerializer

    # TODO: override get_serializer_context

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
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'status': 'success', 'answer_id': serializer.data.get('id')},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = Answer.objects.get(id=kwargs['answer_id'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.context['question_id'] = kwargs.get('question_id')
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_order = instance.order
        instance.delete()
        Question.objects.filter(order__gt=instance_order).update(order=F('order') - 1)
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)


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
    queryset = Survey.objects.all()
    lookup_url_kwarg = 'survey_id'

    def retrieve(self, request, *args, **kwargs):
        """
        # get survey result by its id
        """
        serializer = self.serializer_class(Question.objects.get(id=self.kwargs['question_id']), many=False)
        return Response({'question_result': serializer.data}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        # get result by survey id
        """
        # get all question results for a survey
        result_info_serializer = SurveyResultInfoSerializer(self.queryset.get(id=self.kwargs['survey_id']), many=False)
        items_query = Item.objects.prefetch_related('questions').filter(survey=self.kwargs['survey_id'])
        result_serializer = self.serializer_class(Question.objects.filter(item_id__in=items_query), many=True)
        return Response({'results_info': result_info_serializer.data,
                         'results': result_serializer.data},
                        status=status.HTTP_200_OK)


class SurveyResultFullViewSet(SurveyResultViewSet):
    serializer_class = SurveyResultFullSerializer


class IntervieweeViewSet(ModelViewSet):
    queryset = Interviewee.objects.all()
    serializer_class = IntervieweeSerializer
    lookup_url_kwarg = 'interviewee_id'


class SendEmailViewSet(ModelViewSet):
    queryset = Interviewee.objects.all()

    @action(detail=False, methods=['POST'])
    def send(self, request, *args, **kwargs):
        """
        send a mail with link to survey
        eg. http://127.0.0.1:4200/survey/survey_uuid
        """
        selected_interviewees = request.query_params.get('selected')
        survey_id = kwargs['survey_id']
        survey_title = Survey.objects.get(id=survey_id).title

        if not selected_interviewees:
            try:
                email_list = request.data['interviewees']
                send_my_mass_mail(survey_id, survey_title, email_list)
            except KeyError as e:
                hint = "Provide correct email list eg. {'interviewees': ['abc@gmail.com', 'kpz@pwr.edu.pl']}"
                return Response(
                    {'status': 'error', 'message': e.args, 'hint': hint}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'survey_id': survey_id, 'status': 'error', 'message': e.args},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'survey_id': survey_id, 'status': 'sending process started'},
                            status=status.HTTP_200_OK)

        try:
            interviewees = request.data['interviewees']
            selected_interviewees_emails = \
                [self.queryset.get(id=interviewee_id).email for interviewee_id in interviewees]
            send_my_mass_mail(survey_id, survey_title, selected_interviewees_emails)
        except KeyError as e:
            hint = "Provide correct interviewee id list eg.  " \
                   "{'interviewees': ['7d01d6b3-df2a-42fc-ab9e-ffe5f39a9685', '8e813c93-37a7-429f-926c-0ac092b30c79']}"
            return Response(
                {'status': 'error', 'message': e.args, 'hint': hint}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'survey_id': survey_id, 'status': 'error', 'message': e.args},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'survey_id': survey_id, 'status': 'sending process started'}, status=status.HTTP_200_OK)


class CSVIntervieweesViewSet(ModelViewSet):  # 1. add to db, 2. add to db and send, 3. send without add
    serializer_class = IntervieweeUploadSerializer
    queryset = Interviewee.objects.all()

    @staticmethod
    def get_email_list(already_exists, new_interviewee_list):
        csv_interviewees = already_exists + new_interviewee_list
        return [interviewee.email for interviewee in csv_interviewees]

    @action(detail=False, methods=['POST'])
    def upload_csv(self, request, *args, **kwargs):
        save = request.query_params.get('save')
        survey_id = request.query_params.get('send_survey')

        if not save and not survey_id:
            return Response({'status': 'error', 'message': 'the specified endpoint has no effect',
                             'hint': 'provide available query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        try:
            csv_reader = pd.read_csv(file, sep=';', encoding='utf8')
            new_interviewee_list = []
            already_exists = []
            for idx, row in csv_reader.iterrows():
                new_interviewee = Interviewee(
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                already_exists.append(new_interviewee) if Interviewee.objects.filter(email=row['email']).count() else \
                    new_interviewee_list.append(new_interviewee)
        except pd.errors.EmptyDataError:
            return Response({'status': 'error', 'message': 'selected file is empty or is not .csv',
                             'hint': 'provide CSV with 3 cols with ";" separator eg. email;first_name;last_name'},
                            status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'status': 'error',
                             "message": "selected file doesnt contain 'email', 'first_name' or 'last_name' column",
                             'hint': 'provide CSV with 3 cols: email;first_name;last_name'},
                            status=status.HTTP_400_BAD_REQUEST)

        if survey_id:
            email_list = self.get_email_list(already_exists, new_interviewee_list)
            survey_title = Survey.objects.get(id=survey_id).title
            try:
                send_my_mass_mail(survey_id, survey_title, email_list)
            except Exception as e:
                return Response({'survey_id': survey_id, 'status': 'error during sending email',
                                 'message': e.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if not save:
                return Response({'survey_id': survey_id, 'status': 'sending process started'},
                                status=status.HTTP_200_OK)

            Interviewee.objects.bulk_create(new_interviewee_list)
            return Response(
                {'status': 'respondents saved, sending process started',
                 'newly added': IntervieweeSerializer(new_interviewee_list, many=True).data,
                 'already exists': IntervieweeSerializer(already_exists, many=True).data},  # maybe without existing?
                status=status.HTTP_201_CREATED)

        Interviewee.objects.bulk_create(new_interviewee_list)
        return Response(
            {'status': 'respondents saved',
             'newly added': IntervieweeSerializer(new_interviewee_list, many=True).data,
             'already exists': IntervieweeSerializer(already_exists, many=True).data},  # maybe without existing?
            status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def download_csv(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="interviewees{datetime.datetime.now()}.csv"'
        response.write(u'\ufeff'.encode('utf8'))

        writer = csv.writer(response)

        header = ';'.join(['email', 'first_name', 'last_name'])
        writer.writerow([header])

        for interviewee in self.queryset:
            row = ';'.join([
                interviewee.email,
                interviewee.first_name,
                interviewee.last_name,
            ])
            writer.writerow([row])

        return response


# for Preconditions
class PreconditionViewSet(ModelViewSet):
    serializer_class = PreconditionSerializer
    lookup_url_kwarg = 'precondition_id'
    queryset = Precondition.objects.all()


class QuestionResultRawViewSet(ModelViewSet):
    lookup_url_kwarg = 'question_id'

    def get_queryset(self):
        return Answer.objects.filter(question=Question.objects.get(id=self.kwargs['question_id']))

    def retrieve(self, request, *args, **kwargs):
        question = Question.objects.get(id=self.kwargs['question_id'])
        answer_type = question.get_answer_content_type()
        question_val = question.value[:15].replace('?', '').replace('\\', '').replace('/', '')
        queryset = self.get_queryset()

        q_err = 'Question without item type or with invalid type or question doesnt exist'
        if not answer_type or answer_type not in ['option', 'content_numeric', 'content_character'] or not question_val:
            return Response({'status': 'error', 'message': q_err}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return xlsx_question_charts_file(queryset, question_val, answer_type)


class SurveyResultRawViewSet(ModelViewSet):
    lookup_url_kwarg = 'survey_id'

    def get_queryset(self):
        items_query = Item.objects.prefetch_related('questions').filter(survey=self.kwargs['survey_id'])
        question_query = Question.objects.filter(item_id__in=items_query)
        return question_query

    def get_queryset_combined(self):
        question_query = self.get_queryset()
        combined_queryset = Answer.objects.filter(question__in=question_query).prefetch_related('question')
        return combined_queryset

    def retrieve(self, request, *args, **kwargs):
        survey = Survey.objects.get(id=self.kwargs['survey_id'])
        survey_title = survey.title[:15].replace('?', '').replace('\\', '').replace('/', '')
        return xlsx_survey_results(self.get_queryset(), survey_title)
        # zapytać InsERT które poejście lepsze (2 zapytania do bazy i dict czy zapytanie o Answers co każde Question
        # wbrew pozorom pierwsze może zająć dużo pamięci przy ogromnej ilości danych, drugie z kolei spam do bazy
        # ewentualnie dać parametr do wywołania funkcji, którą chcemy
        # return xlsx_survey_results2(self.get_queryset(), self.get_queryset_combined(), survey_title)
