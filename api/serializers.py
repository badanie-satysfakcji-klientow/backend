from rest_framework import serializers
from .models import Answers, Creators, CreatorsInterviewees, Interviewees, Items, Options, OptionsItems,\
    Questions, Sections, SurveySent, SurveySubmissions, Surveys, SurveysItems #, Preconditions


class SurveysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Surveys
        fields = '__all__'
