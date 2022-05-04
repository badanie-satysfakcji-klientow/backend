from rest_framework import serializers
from .models import Answer, Creator, \
    Interviewee, Item, Option, Precondition, \
    Question, Section, SurveySent, SurveySubmission, Survey, OptionItem


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
        ret = super(SurveySerializer, self).to_representation(instance)

        # extra fields

        items = Item.objects.all()
        items_serializer = ItemSerializer(items, many=True)
        ret['items'] = items_serializer.data

        sections = Section.objects.all()
        sections_serializer = SectionSerializer(sections, many=True)
        ret['sections'] = sections_serializer.data
        return ret


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'section', 'header', 'questions']

    def to_representation(self, instance):
        ret = super(ItemSerializer, self).to_representation(instance)

        # extra fields
        questions = Question.objects.filter(item_id=instance.id)
        questions_serializer = QuestionSerializer(questions, many=True)
        ret['questions'] = questions_serializer.data

        option_ids = OptionItem.objects.filter(item_id=instance.id).values('option_id')
        optionsitems_serializer = OptionItemSerializer(option_ids, many=True)
        ret['options'] = optionsitems_serializer.data

        preconditions = Precondition.objects.filter(item_id=instance.id)
        preconditions_serializer = PreconditionSerializer(preconditions, many=True)
        if len(preconditions_serializer.data) > 0:
            ret['preconditions'] = preconditions_serializer.data

        return ret


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('order', 'value')


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
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
        fields = ('expected_option', 'next_item')


class OptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionItem
        fields = ('option_id', 'item_id')
