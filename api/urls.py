from django.urls import path
from .views import ItemViewSet,  SurveyViewSet

urlpatterns = [

    path('api/surveys/<uuid:survey_id>/items', ItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/surveys/<uuid:survey_id>', SurveyViewSet.as_view({'get': 'retrieve', 'put': 'update',
                                                                'patch': 'partial_update', 'delete': 'destroy'})),
    path('api/surveys', SurveyViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/surveys/send', SurveyViewSet.as_view({'post': 'send'})),
]
