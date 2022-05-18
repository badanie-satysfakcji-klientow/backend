from rest_framework import serializers
from .models import Answer, Creator, \
    Interviewee, Item, Option, Precondition, \
    Question, Section, SurveySent, SurveySubmission, Survey


class SurveyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'created_at', 'anonymous', 'starts_at', 'expires_at')

    def to_representation(self, instance):
        ret = super(SurveyInfoSerializer, self).to_representation(instance)

        #extra fields
        questions_count = Item.objects.filter(survey_id=instance.id).count()
        ret['questions_count'] = questions_count
        return ret


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('id',
                  'title',
                  'description',
                  'creator_id',
                  'created_at',
                  'starts_at',
                  'expires_at',
                  'paused',
                  'anonymous',
                  'greeting',
                  'farewell')


class ItemSerializer(serializers.ModelSerializer):
    type_map = {
        1: 'list',
        2: 'gridSingle',
        3: 'gridMultiple',
        4: 'scale5',
        5: 'scale10',
        6: 'scaleNPS',
        7: 'openShort',
        8: 'openLong',
        9: 'openNumeric',
        10: 'closedSingle',
        11: 'closedMultiple'
    }

    class Meta:
        model = Item
        fields = ['id', 'section', 'header', 'type', 'questions']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'order', 'value')


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'content']


class ItemSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    options = OptionSerializer(many=True)

    class Meta:
        model = Item
        fields = ['id', 'header', 'type', 'required', 'questions', 'options']

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        options = validated_data.pop('options')
        validated_data['survey_id'] = self.context['survey_id']
        item = Item.objects.create(**validated_data)
        for question in questions:
            Question.objects.create(item=item, **question)
        for option in options:
            Option.objects.create(item=item, **option)
        return item


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('title', 'description')

    def to_representation(self, instance):
        ret = super(SectionSerializer, self).to_representation(instance)

        # extra fields
        items = Item.objects.filter(survey_id=instance.id)
        items_serializer = ItemSerializer(items, many=True)
        return ret


class PreconditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precondition
        fields = ('expected_option', 'next_item')
