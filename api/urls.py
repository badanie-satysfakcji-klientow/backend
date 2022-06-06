from django.urls import path
from .views import ItemViewSet, SurveyViewSet, QuestionViewSet, OptionViewSet

urlpatterns = [
    path('api/items/<uuid:item_id>', ItemViewSet.as_view({'put': 'update', 'patch': 'partial_update'})),
    path('api/questions/<uuid:question_id>', QuestionViewSet.as_view({'patch': 'partial_update'})),
    path('api/options/<uuid:option_id>', OptionViewSet.as_view({'patch': 'partial_update'})),
    path('api/items', ItemViewSet.as_view({'get': 'list'})),
    path('api/surveys', SurveyViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/surveys/<uuid:survey_id>', SurveyViewSet.as_view({'get': 'retrieve', 'put': 'update',
                                                                'patch': 'partial_update', 'delete': 'destroy'})),
    path('api/surveys/<uuid:survey_id>/items', ItemViewSet.as_view({'get': 'list', 'post': 'create'})),
]
