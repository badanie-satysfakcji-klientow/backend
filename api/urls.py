from django.urls import path
from .views import ItemViewSet, SurveyViewSet, AnswerViewSet, SubmissionViewSet, SectionViewSet, \
    QuestionViewSet, OptionViewSet, AnswersCountViewSet, SurveyResultViewSet, SendEmailViewSet, \
    IntervieweeViewSet, CSVIntervieweesViewSet, SurveyResultFullViewSet, PreconditionViewSet, \
    SurveyResultRawViewSet, QuestionResultRawViewSet, CreatorViewSet


urlpatterns = [
    path('api/surveys/<uuid:survey_id>/items',
         ItemViewSet.as_view({'post': 'create'}), name='survey-items'),
    path('api/surveys/<uuid:survey_id>/sections',
         SectionViewSet.as_view({'get': 'list', 'post': 'create'}), name='sections'),
    path('api/surveys/<uuid:survey_id>/send', SendEmailViewSet.as_view({'post': 'send'}), name='send-manually'),
    path('api/surveys/<uuid:survey_id>/submit', SubmissionViewSet.as_view({'post': 'create'}), name='submit'),
    path('api/surveys/<uuid:survey_id>/submissions',
         AnswersCountViewSet.as_view({'get': 'list'}), name='submissions-get-count'),
    path('api/surveys/<uuid:survey_id>/results', SurveyResultViewSet.as_view({'get': 'list'}), name='results'),
    path('api/surveys/<uuid:survey_id>/results/raw',
         SurveyResultRawViewSet.as_view({'get': 'retrieve'}), name='results-raw'),
    path('api/surveys/<uuid:survey_id>/preconditions',
         PreconditionViewSet.as_view({'get': 'list'}), name='preconditions-get'),
    path('api/surveys/<uuid:survey_id>',
         SurveyViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='surveys-uuid'),
    path('api/surveys', SurveyViewSet.as_view({'post': 'create'}), name='surveys'),

    path('api/items/<uuid:item_id>',
         ItemViewSet.as_view({'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='items-uuid'),
    # path('api/items', ItemViewSet.as_view({'get': 'list'})),

    path('api/questions/<uuid:question_id>/answer', AnswerViewSet.as_view({'post': 'create'}), name='questions-answer'),
    path('api/questions/<uuid:question_id>/answer/<uuid:answer_id>',
         AnswerViewSet.as_view({'patch': 'partial_update'}), name='questions-answer-update'),
    path('api/questions/<uuid:question_id>/results',
         SurveyResultViewSet.as_view({'get': 'retrieve'}), name='question-results'),
    path('api/questions/<uuid:question_id>/results/more',
         SurveyResultFullViewSet.as_view({'get': 'retrieve'}), name='question-results-full'),
    path('api/questions/<uuid:question_id>/results/raw',
         QuestionResultRawViewSet.as_view({'get': 'retrieve'}), name='question-results-raw'),
    path('api/questions/<uuid:question_id>',
         QuestionViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='questions-uuid'),

    path('api/options/<uuid:option_id>',
         OptionViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='options-uuid'),

    path('api/creators/<uuid:creator_id>/surveys',
         SurveyViewSet.as_view({'get': 'retrieve_brief'}), name='surveys-brief-info'),
    path('api/creators/<uuid:creator_id>',
         CreatorViewSet.as_view({'get': 'retrieve', 'patch': 'check_partial_update', 'delete': 'check_destroy'}),
         name='creator-uuid'),
    path('api/creators',
         CreatorViewSet.as_view({'post': 'create'}), name='creator'),

    path('api/interviewees/<uuid:interviewee_id>',
         IntervieweeViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy', 'get': 'retrieve'}),
         name='interviewee-uuid'),
    path('api/interviewees',
         IntervieweeViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='interviewee'),
    path('api/interviewees/csv',
         CSVIntervieweesViewSet.as_view({'get': 'download_csv', 'post': 'upload_csv'}),
         name='interviewee-csv'),

    path('api/preconditions/<uuid:precondition_id>',
         PreconditionViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='preconditions-uuid'),
    path('api/preconditions',
         PreconditionViewSet.as_view({'post': 'create'}), name='preconditions'),

]

# non anonymous requires login

# tokenized_urls (anonymous survey)
urlpatterns += [
    path('api/surveys/<str:survey_hash>/sections',
         SectionViewSet.as_view({'get': 'anonymous_list'}), name='sections-anonymous'),
    path('api/surveys/<str:survey_hash>/submit',
         SubmissionViewSet.as_view({'post': 'anonymous_create'}), name='submit-anonymous'),
    path('api/surveys/<str:survey_hash>',
         SurveyViewSet.as_view({'get': 'anonymous_retrieve'}), name='surveys-anonymous'),  # should not be used
]
