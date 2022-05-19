from django.db.models import Max
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


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'order', 'value')


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'content']


class ItemSerializer(serializers.ModelSerializer):
    questions = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
    options = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)

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
        fields = ['id', 'required', 'questions', 'options']

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        options = validated_data.pop('options')
        validated_data['survey_id'] = self.context['survey_id']
        type_map_key = [key for key, value in self.type_map.items() if value == self.context['type']][0]
        validated_data['type'] = type_map_key
        item = Item.objects.create(**validated_data)
        if questions:
            # get max order index from questions in survey
            survey_items = Item.objects.filter(survey_id=self.context['survey_id'])
            max_order = Question.objects.filter(item_id__in=survey_items).aggregate(max_order=Max('order'))['max_order'] or 0
            self.context['questions'] = []
            for question in questions:
                max_order += 1
                obj = {'item_id': item.id, 'order': max_order, 'value': question}
                question = Question.objects.create(**obj)
                self.context.get('questions').append(question)

        if options:
            for option in options:
                Option.objects.create(**{'item_id': item.id, 'content': option})

        return item


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ('title', 'description')

    def get_items(self, obj):
        return ItemSerializer(Item.objects.filter(survey_id=obj.id), many=True).data


class PreconditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precondition
        fields = ('expected_option', 'next_item')
