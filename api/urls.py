from django.urls import path, include
from rest_framework_nested import routers

from .views import ItemViewSet, SurveyViewSet, AnswerViewSet, SubmissionViewSet, SectionViewSet, \
    QuestionViewSet, OptionViewSet, AnswersCountViewSet, SurveyResultViewSet, SendEmailViewSet, \
    IntervieweeViewSet, CSVIntervieweesViewSet, SurveyResultFullViewSet, PreconditionViewSet, \
    SurveyResultRawViewSet, QuestionResultRawViewSet, CreatorViewSet

survey_router = routers.SimpleRouter(trailing_slash=False)
survey_router.register(r'surveys', SurveyViewSet)

interviewee_router = routers.SimpleRouter(trailing_slash=False)
interviewee_router.register(r'interviewees', IntervieweeViewSet)

question_router = routers.SimpleRouter(trailing_slash=False)
question_router.register(r'questions', QuestionViewSet)

creator_router = routers.SimpleRouter(trailing_slash=False)
creator_router.register(r'creators', CreatorViewSet)

answer_router = routers.NestedSimpleRouter(
    question_router,
    r'questions',
    lookup='question'
)
answer_router.register(r'answers', AnswerViewSet)

interviewee_csv_router = routers.NestedSimpleRouter(
    creator_router,
    r'creators',
    lookup='creator'
)
interviewee_csv_router.register(r'intervieweescsv', CSVIntervieweesViewSet)

items_router = routers.NestedSimpleRouter(
    survey_router,
    r'surveys',
    lookup='survey'
)
items_router.register(r'items', ItemViewSet)

precondition_router = routers.NestedSimpleRouter(
    survey_router,
    r'surveys',
    lookup='survey'
)
precondition_router.register(r'preconditions', PreconditionViewSet)

# uncomment when creator CRUD added
# creator_nested_router = routers.NestedSimpleRouter(
#     creator_router,
#     r'creators',
#     lookup='creator'
# )
# creator_nested_router.register(r'interviewees-csv', CSVIntervieweesViewSet, basename='interviewees-csv')

# routed
urlpatterns = [
    # surveys
    path('api/', include(survey_router.urls)),
    # answers
    path('api/', include(answer_router.urls)),
    # questions
    path('api/', include(question_router.urls)),
    # items
    path('api/', include(items_router.urls)),
    # preconditions
    path('api/', include(precondition_router.urls)),
    # interviewees
    path('api/', include(interviewee_router.urls)),
    # creators
    path('api/', include(creator_router.urls)),
    # interviewees csv
    path('api/', include(interviewee_csv_router.urls)),
]

# non routed
urlpatterns += [
    # sections
    path('api/surveys/<uuid:survey_id>/sections',
         SectionViewSet.as_view({'get': 'list', 'post': 'create'}), name='sections'),

    # submissions
    # TODO: check if can be merged in one viewset
    path('api/surveys/<uuid:survey_id>/submit', SubmissionViewSet.as_view({'post': 'create'}), name='submit'),
    path('api/surveys/<uuid:survey_id>/submissions',
         AnswersCountViewSet.as_view({'get': 'list'}), name='submissions-get-count'),

    # results
    path('api/questions/<uuid:question_id>/results',
         SurveyResultViewSet.as_view({'get': 'retrieve'}), name='question-results'),
    path('api/questions/<uuid:question_id>/results/more',
         SurveyResultFullViewSet.as_view({'get': 'retrieve'}), name='question-results-full'),
    path('api/questions/<uuid:question_id>/results/raw',
         QuestionResultRawViewSet.as_view({'get': 'retrieve'}), name='question-results-raw'),
    path('api/surveys/<uuid:survey_id>/results', SurveyResultViewSet.as_view({'get': 'list'}), name='results'),
    path('api/surveys/<uuid:survey_id>/results/raw',
         SurveyResultRawViewSet.as_view({'get': 'retrieve'}), name='results-raw'),

    # options
    path('api/options/<uuid:option_id>',
         OptionViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='options-uuid'),

    # surveys by creator
    path('api/creators/<uuid:creator_id>/surveys',
         SurveyViewSet.as_view({'get': 'retrieve_brief'}), name='surveys-brief-info'),

    # interviewees
    # TODO: download i upload powinny być na
    #   api/creators/<uuid:creator_id>/interviewees (nie musi być /csv na końcu)
    # path('api/interviewees/csv',
    #      CSVIntervieweesViewSet.as_view({'get': 'download_csv', 'post': 'upload_csv'}),
    #      name='interviewee-csv'),


    # path('api/creators/<uuid:creator_id>/interviewees-csv',
    #      CSVIntervieweesViewSet.as_view({'post': 'upload_csv', 'get': 'download_csv'}), name='interviewee-csv'),

    # uncomment and move to previous urlpatterns when creator CRUD added
    # path('api/', include(creator_router.urls)),
    # path('api/', include(interviewee_csv_router.urls)),

    # send email
    path('api/surveys/<uuid:survey_id>/send', SendEmailViewSet.as_view({'post': 'send'}), name='send-manually'),
]
