from django.db.models import Max
from rest_framework import serializers
from .models import Answer, Creator, \
    Interviewee, Item, Option, Precondition, \
    Question, Section, SurveySent, Submission, Survey


class SurveyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'created_at', 'anonymous', 'starts_at', 'expires_at')

    def to_representation(self, instance):
        ret = super(SurveyInfoSerializer, self).to_representation(instance)

        # extra fields
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


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'interviewee']
        read_only_fields = ['submitted_at', 'survey']

    def validate(self, attrs):
        attrs['survey'] = Survey.objects.filter(id=self.context['survey_id']).first()

        # check if user already submitted
        if Submission.objects.filter(survey_id=attrs['survey'].id, interviewee=attrs['interviewee'].id).exists():
            raise serializers.ValidationError('User already submitted')
        return attrs


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'content_numeric', 'content_character', 'option', 'submission']
        read_only_fields = ['question']

    def del_attrs(self, attrs, attr_list):
        for attr in attr_list:
            if hasattr(attrs, attr):
                delattr(attrs, attr)
        return attrs

    def validate(self, attrs):
        attrs['question'] = Question.objects.filter(id=self.context['question_id']).first()
        # check if survey_submission contains the question
        item_id = Question.objects.filter(id=attrs['question'].id).first().item_id
        survey_id = Submission.objects.filter(id=attrs['submission'].id).first().survey_id
        objects = Item.objects.filter(survey_id=survey_id).values_list('id', flat=True)
        if item_id not in objects:
            raise serializers.ValidationError('Question not found in survey')

        # check if survey is paused
        if Survey.objects.filter(id=survey_id).first().paused:
            raise serializers.ValidationError('Survey is paused')

        # check for item type
        item_type = ItemSerializer.type_map[Item.objects.filter(id=item_id).first().type]

        if item_type in ['list', 'gridSingle', 'gridMultiple', 'closedSingle', 'closedMultiple']:
            if not attrs['option']:
                raise serializers.ValidationError('Option is required')
            self.del_attrs(attrs, ['content_numeric', 'content_character'])
        elif item_type in ['openShort', 'openLong']:
            if not attrs['content_character']:
                raise serializers.ValidationError('Content is required')
            self.del_attrs(attrs, ['content_numeric', 'option'])
        else:
            if not attrs['content_numeric']:
                raise serializers.ValidationError('Content is required')
            self.del_attrs(attrs, ['option', 'content_character'])
        return attrs

    def create(self, validated_data):
        validated_data['question_id'] = self.context['question_id']
        answer = Answer.objects.create(**validated_data)
        return answer


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
