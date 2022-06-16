from django.urls import path

from .views import ItemViewSet, SurveyViewSet, AnswerViewSet, SubmissionViewSet, SectionViewSet, \
    QuestionViewSet, OptionViewSet, AnswersCountViewSet

urlpatterns = [
    path('api/surveys/<uuid:survey_id>/items',
         ItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='survey-items'),
    path('api/surveys/<uuid:survey_id>/sections',
         SectionViewSet.as_view({'get': 'list', 'post': 'create'}), name='sections'),
    path('api/surveys/<uuid:survey_id>/send', SurveyViewSet.as_view({'post': 'send'})),
    path('api/surveys/<uuid:survey_id>/submit', SubmissionViewSet.as_view({'post': 'create'}), name='submit'),
    path('api/surveys/<uuid:survey_id>/submissions',
         AnswersCountViewSet.as_view({'get': 'list'}), name='submissions-get-count'),
    path('api/surveys/<uuid:survey_id>',
         SurveyViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='surveys-uuid'),
    path('api/surveys', SurveyViewSet.as_view({'get': 'list', 'post': 'create'}), name='surveys'),
    path('api/items/<uuid:item_id>',
         ItemViewSet.as_view({'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='items-uuid'),
    # path('api/items', ItemViewSet.as_view({'get': 'list'})),
    path('api/questions/<uuid:question_id>/answer', AnswerViewSet.as_view({'post': 'create'}), name='questions-answer'),
    path('api/questions/<uuid:question_id>', QuestionViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})),
    path('api/options/<uuid:option_id>', OptionViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='options-uuid'),
    path('api/creators/<uuid:creator_id>/surveys',
         SurveyViewSet.as_view({'get': 'retrieve_brief'}), name='surveys-brief-info')
]
