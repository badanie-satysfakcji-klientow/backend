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

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # # extra fields
        sections = Section.objects.all()
        sections_serializer = SectionSerializer(sections, many=True)
        ret['sections'] = sections_serializer.data

        # ret['sections'] = sections_serializer.data
        return ret


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
        fields = ['id', 'type', 'required', 'questions', 'options']

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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['type'] = self.type_map[ret['type']]

        # extra fields
        questions = Question.objects.filter(item_id=instance.id)
        questions_serializer = QuestionSerializer(questions, many=True)
        ret['questions'] = questions_serializer.data

        options = Option.objects.filter(item_id=instance.id)
        options_serializer = OptionSerializer(options, many=True)
        ret['options'] = options_serializer.data

        preconditions = Precondition.objects.filter(item_id=instance.id)
        preconditions_serializer = PreconditionSerializer(preconditions, many=True)
        if len(preconditions_serializer.data) > 0:
            ret['preconditions'] = preconditions_serializer.data

        return ret


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('title', 'description')

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # extra fields
        items = Item.objects.filter(section_id=instance.id)
        items_serializer = ItemSerializer(items, many=True)
        ret['items'] = items_serializer.data

        return ret


class PreconditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precondition
        fields = ('expected_option', 'next_item')
