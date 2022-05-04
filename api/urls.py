from django.urls import path
from . import views


urlpatterns = [
    path('api/v1/surveys', views.SurveysList.as_view()),
]
