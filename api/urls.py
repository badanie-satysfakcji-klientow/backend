from django.urls import path
from .views import ItemViewSet,  SurveyViewSet, AnswerViewSet, SubmissionViewSet


urlpatterns = [
    path('api/surveys/<uuid:survey_id>/items', ItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/surveys/<uuid:survey_id>/submit', SubmissionViewSet.as_view({'post': 'create'})),
    path('api/questions/<uuid:question_id>/answer', AnswerViewSet.as_view({'post': 'create'})),
    path('api/surveys/<uuid:survey_id>', SurveyViewSet.as_view({'get': 'retrieve', 'put': 'update',
                                                                'patch': 'partial_update', 'delete': 'destroy'})),
    path('api/surveys', SurveyViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/surveys/<uuid:survey_id>/sections', SectionViewSet.as_view({'get': 'list', 'post': 'create'})),
]
