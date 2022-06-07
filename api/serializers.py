from rest_framework import serializers
from .models import Answer, Creator, \
    Interviewee, Item, Option, Precondition, \
    Question, Section, SurveySent, SurveySubmission, Survey


class SurveyInfoSerializer(serializers.ModelSerializer):
    sections_count = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'created_at', 'anonymous', 'starts_at', 'expires_at', 'paused',
                  'sections_count', 'items_count', 'questions_count')

    def get_sections_count(self, instance):
        items_list = Item.objects.filter(survey_id=instance.id).values_list('id', flat=True)
        return Section.objects.filter(start_item_id__in=items_list).count()

    def get_items_count(self, instance):
        return Item.objects.filter(survey_id=instance.id).count()

    def get_questions_count(self, instance):
        items_list = Item.objects.filter(survey_id=instance.id).values_list('id', flat=True)
        return Question.objects.filter(item_id__in=items_list).count()


class SurveySerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField(read_only=True)
    items = serializers.SerializerMethodField(read_only=True)

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
                  'farewell',
                  'items',
                  'sections',
                  )

    def get_sections(self, instance):
        sections = Survey.objects.get(id=instance.id).get_sections_in_order()
        sections_serializer = SectionSerializer(sections, many=True)
        return sections_serializer.data

    def get_items(self, instance):
        items = Survey.objects.get(id=instance.id).get_items_in_order()
        items_serializer = ItemSerializer(items, many=True)
        if len(items_serializer.data) > 0:
            return items_serializer.data


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
    preconditions = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id', 'type', 'required', 'questions', 'options', 'preconditions']

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

    def get_type(self, instance):
        return self.type_map[instance.type]

    def get_questions(self, instance):
        questions = Question.objects.filter(item_id=instance.id).order_by('order')
        return QuestionSerializer(questions, many=True).data

    def get_options(self, instance):
        options = Option.objects.filter(item_id=instance.id)
        return OptionSerializer(options, many=True).data

    def get_preconditions(self, instance):
        preconditions = Precondition.objects.filter(item_id=instance.id)
        preconditions_serializer = PreconditionSerializer(preconditions, many=True)
        if len(preconditions_serializer.data) > 0:
            return preconditions_serializer.data


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['title', 'description', 'start_item', 'end_item']


class PreconditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precondition
        fields = ('expected_option', 'next_item')
