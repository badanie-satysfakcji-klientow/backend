from collections import Counter

from django.db.models import Max, Count, Avg
from rest_framework import serializers
from .models import Answer, Item, Option, Precondition, Question, Section, Submission, Survey, Interviewee


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
        sections = instance.get_sections_in_order()
        sections_serializer = SectionSerializer(sections, many=True)
        if len(sections_serializer.data) > 0:
            return sections_serializer.data

    def get_items(self, instance):
        items = instance.get_items_in_order()
        items_serializer = ItemGetSerializer(items, many=True)
        if len(items_serializer.data) > 0:
            return items_serializer.data


class SurveyInfoSerializer(SurveySerializer):
    sections = None
    items = None

    class Meta(SurveySerializer.Meta):
        fields = ('id', 'title', 'description', 'created_at', 'anonymous', 'starts_at', 'expires_at', 'paused')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'order', 'value')


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'content']


class AnswerQuestionCountSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'order', 'value', 'count')

    def get_count(self, instance):
        return Answer.objects.filter(question_id=instance.id).count()


class ItemSerializer(serializers.ModelSerializer):
    questions = serializers.ListSerializer(child=serializers.CharField(), allow_null=True, required=False)
    options = serializers.ListSerializer(child=serializers.CharField(), allow_null=True, required=False)
    type = serializers.SerializerMethodField()

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

    def get_type(self, instance):
        return self.type_map[instance.type]

    inv_type_map = {v: k for k, v in type_map.items()}

    content_map = {
        ('list', 'gridSingle', 'gridMultiple', 'closedSingle', 'closedMultiple'): 'option',
        ('openShort', 'openLong'): 'content_character',
        ('scale5', 'scale10', 'scaleNPS', 'openNumeric'): 'content_numeric'
    }

    inv_content_map = {v: k for k, v in content_map.items()}

    class Meta:
        model = Item
        fields = ['id', 'required', 'type', 'questions', 'options']

    def get_type_display(self, obj) -> int:
        return [key for key, value in self.type_map.items() if value == self.context['type']][0]

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        # case when no option is needed (e.g. numeric)
        try:
            options = validated_data.pop('options')
        except KeyError:
            options = None
        validated_data['survey_id'] = self.context['survey_id']
        validated_data['type'] = self.inv_type_map[self.context['type']]
        item = Item.objects.create(**validated_data)
        if questions:
            # get max order index from questions in survey
            survey_items = Item.objects.filter(survey_id=self.context['survey_id'])
            max_order = Question.objects.filter(item_id__in=survey_items) \
                .aggregate(max_order=Max('order'))['max_order'] or 0
            self.context['questions'] = {}
            questions = Question.objects \
                .bulk_create([Question(item_id=item.id, order=max_order + 1, value=question) for question in questions])

            for question in questions:
                self.context['questions'][question.order] = question.id

        if options:
            Option.objects.bulk_create([Option(item_id=item.id, content=option) for option in options])

        return item

    def update(self, instance, validated_data):
        if self.context['type']:
            type_map_key = [key for key, value in self.type_map.items() if value == self.context['type']][0]
            validated_data['type'] = type_map_key
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance


class ItemGetSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    options = OptionSerializer(many=True)
    preconditions = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id', 'required', 'questions', 'options', 'preconditions', 'type']

    def get_type(self, instance):
        return ItemSerializer.type_map[instance.type]

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


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'interviewee']
        read_only_fields = ['submitted_at', 'survey']

    def validate(self, attrs):
        attrs['survey'] = Survey.objects.get(id=self.context['survey_id'])
        # check if user already submitted
        if Submission.objects.filter(survey_id=attrs['survey'].id, interviewee=attrs['interviewee'].id).exists():
            raise serializers.ValidationError('User already submitted')
        return attrs


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'content_numeric', 'content_character', 'option', 'submission']
        read_only_fields = ['question']

    @staticmethod
    def del_attrs(attrs, attr_list):
        for attr in attr_list:
            if hasattr(attrs, attr):
                delattr(attrs, attr)
        return attrs

    def validate(self, attrs):
        # TODO: check if question exists
        attrs['question'] = Question.objects.get(id=self.context['question_id'])
        # check if survey_submission contains the question
        item_id = Question.objects.get(id=attrs['question'].id).item_id
        survey_id = Submission.objects.get(id=attrs['submission'].id).survey_id
        objects = Item.objects.filter(survey_id=survey_id).values_list('id', flat=True)
        if item_id not in objects:
            raise serializers.ValidationError('Question not found in survey')

        # check if survey is paused
        if Survey.objects.get(id=survey_id).paused:
            raise serializers.ValidationError('Survey is paused')

        # check for item type
        item_type = ItemSerializer.type_map[Item.objects.get(id=item_id).type]

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


class SurveyResultInfoSerializer(serializers.ModelSerializer):
    answers_count = serializers.SerializerMethodField()
    submissions_count = serializers.SerializerMethodField()

    # TODO: Think of some other needed fields
    class Meta:
        model = Survey
        fields = ['answers_count', 'submissions_count']

    def get_submissions_count(self, instance):
        return Submission.objects.filter(survey_id=instance.id).count()

    def get_answers_count(self, instance):
        submissions_query = Submission.objects.filter(survey_id=instance.id).values_list('id', flat=True)
        return Answer.objects.filter(submission_id__in=submissions_query).count()


class SurveyResultSerializer(serializers.ModelSerializer):
    # fields for option
    # options_count = serializers.SerializerMethodField()
    # fields for content_character
    common_answers = serializers.SerializerMethodField()
    # fields for content_numeric
    mean = serializers.SerializerMethodField()
    answers_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'order', 'value', 'mean', 'answers_count', 'common_answers']

    def get_common_words(self, instance):
        query = Answer.objects.filter(question_id=instance.id).values_list('content_character', flat=True)
        return Counter(query).most_common(10)

    def get_mean(self, instance):
        count_query = Answer.objects.filter(question_id=instance.id).aggregate(Avg('content_numeric'))
        return count_query['content_numeric__avg']

    def get_common_answers(self, instance):
        sentences = Answer.objects.filter(question_id=instance.id).values_list('content_character', flat=True)
        sentences = [' '.join(content_character.lower().strip().split()) for content_character in sentences]
        return Counter(sentences).most_common(10)

    def get_answers_count(self, instance):
        q_type = ItemSerializer.type_map[instance.item.type]
        if q_type in ItemSerializer.inv_content_map['option']:
            return Answer.objects.select_related('answer_options').filter(question_id=instance.id) \
                .values('option_id') \
                .order_by('option_id') \
                .annotate(count=Count('option_id'))
        elif q_type in ItemSerializer.inv_content_map['content_numeric']:
            return Answer.objects.filter(question_id=instance.id) \
                .values('content_numeric') \
                .order_by('content_numeric') \
                .annotate(count=Count('content_numeric'))
        return None


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'start_item', 'end_item', 'title', 'description']

    def validate(self, attrs):
        survey_id = self.context['survey_id']

        if not Item.objects.filter(survey_id=survey_id, id=attrs['start_item'].id).exists():
            raise serializers.ValidationError('Start item not found')
        if not Item.objects.filter(survey_id=survey_id, id=attrs['end_item'].id).exists():
            raise serializers.ValidationError('End item not found')

        # check if start_item is before end_item
        if not (start_item_order := Question.objects.get(item_id=attrs['start_item'].id).order) <= \
               (end_item_order := Question.objects.get(item_id=attrs['end_item'].id).order):
            raise serializers.ValidationError('Start item must be before or equal to end item')

        # check if sections overlap
        sections = Section.objects.prefetch_related('items') \
            .filter(start_item_id__in=Item.objects.filter(survey_id=survey_id).only('id'))

        for section in sections:
            section.start_item_order = Question.objects.get(item_id=section.start_item_id).order
            section.end_item_order = Question.objects.get(item_id=section.end_item_id).order
            if section.start_item_order <= start_item_order <= section.end_item_order or \
                    section.start_item_order <= end_item_order <= section.end_item_order:
                raise serializers.ValidationError('Sections overlap')

        return attrs

    # TODO: section update
    # def update(self, instance, validated_data):
    #     pass


class PreconditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precondition
        fields = ('expected_option', 'next_item')


class IntervieweeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interviewee
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = []


class IntervieweeUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ['file']
