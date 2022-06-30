from django.urls import path, include
from rest_framework_nested import routers

from .views import ItemViewSet, SurveyViewSet, AnswerViewSet, SubmissionViewSet, SectionViewSet, \
    QuestionViewSet, OptionViewSet, AnswersCountViewSet, SurveyResultViewSet, SendEmailViewSet, \
    IntervieweeViewSet, CSVIntervieweesViewSet, SurveyResultFullViewSet, PreconditionViewSet, \
    SurveyResultRawViewSet, QuestionResultRawViewSet, CreatorViewSet, AnonymousSubmissionViewSet

survey_router = routers.SimpleRouter(trailing_slash=False)
survey_router.register(r'surveys', SurveyViewSet)

interviewee_router = routers.SimpleRouter(trailing_slash=False)
interviewee_router.register(r'interviewees', IntervieweeViewSet)

question_router = routers.SimpleRouter(trailing_slash=False)
question_router.register(r'questions', QuestionViewSet)

creator_router = routers.SimpleRouter(trailing_slash=False)
creator_router.register(r'creators', CreatorViewSet)

option_router = routers.SimpleRouter(trailing_slash=False)
option_router.register(r'options', OptionViewSet)

answer_router = routers.NestedSimpleRouter(
    question_router,
    r'questions',
    lookup='question'
)
answer_router.register(r'answers', AnswerViewSet)

creator_nested_router = routers.NestedSimpleRouter(
    creator_router,
    r'creators',
    lookup='creator'
)
creator_nested_router.register(r'interviewees-csv', CSVIntervieweesViewSet, basename='interviewees-csv')
creator_nested_router.register('surveys', SurveyViewSet, basename='surveys-brief')

survey_nested_router = routers.NestedSimpleRouter(
    survey_router,
    r'surveys',
    lookup='survey'
)
survey_nested_router.register(r'items', ItemViewSet)
survey_nested_router.register(r'preconditions', PreconditionViewSet)
survey_nested_router.register(r'sections', SectionViewSet)
survey_nested_router.register(r'submit', SubmissionViewSet, basename='submit')
survey_nested_router.register(r'submissions', AnswersCountViewSet, basename='submission')
survey_nested_router.register(r'send', SendEmailViewSet, basename='send')  # may change that to decorated method in view

# routed
urlpatterns = [
    # surveys
    path('api/', include(survey_router.urls)),
    # answers
    path('api/', include(answer_router.urls)),
    # questions
    path('api/', include(question_router.urls)),
    # preconditions
    path('api/', include(survey_nested_router.urls)),
    # interviewees
    path('api/', include(interviewee_router.urls)),
    # creators
    path('api/', include(creator_router.urls)),
    # options
    path('api/', include(option_router.urls)),
    # interviewees csv
    path('api/', include(creator_nested_router.urls)),  # TODO: <- failing some tests - resolve
]

# non routed
urlpatterns += [
    # TODO: route that
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
]

# tokenized_urls (anonymous survey), TODO: replace surveys-h with surveys in the future
urlpatterns += [
    path('api/surveys-h/<str:survey_hash>/sections',
         SectionViewSet.as_view({'get': 'list'}), name='sections-anonymous'),
    path('api/surveys-h/<str:survey_hash>/submit',
         AnonymousSubmissionViewSet.as_view({'post': 'create'}), name='submit-anonymous'),
    path('api/surveys-h/<str:survey_hash>',
         SurveyViewSet.as_view({'get': 'anonymous_retrieve'}), name='surveys-anonymous'),  # should not be used
]
