from rest_framework import serializers
from .models import Answer, Creator, \
    Interviewee, Item, Option, Precondition, Question, Section, SurveySent, SurveySubmission, Survey


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'items', 'preconditions']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'survey_id', 'section', 'header', 'questions']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'


class PreconditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precondition
        fields = '__all__'
