from django.db.models import Max
from rest_framework import serializers
from .models import Answer, Creator, \
    Interviewee, Item, Option, Precondition, \
    Question, Section, SurveySent, Submission, Survey


class SurveyInfoSerializer(serializers.ModelSerializer):
    sections_count = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        lookup_field = 'survey_id'
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
        if len(sections_serializer.data) > 0:
            return sections_serializer.data

    def get_items(self, instance):
        items = Survey.objects.get(id=instance.id).get_items_in_order()
        items_serializer = ItemGetSerializer(items, many=True)
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


class ItemPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'survey', 'section', 'type', 'required']


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

    def get_type_display(self, obj) -> int:
        return [key for key, value in self.type_map.items() if value == self.context['type']][0]

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

    def update(self, instance, validated_data):
        questions = validated_data.pop('questions')
        options = validated_data.pop('options')
        type_map_key = [key for key, value in self.type_map.items() if value == self.context['type']][0]
        validated_data['type'] = type_map_key
        if questions:
            Question.objects.filter(item=instance).delete()
            Question.objects.bulk_create([Question(item=instance, **q) for q in questions])
        if options:
            Option.objects.filter(item=instance).delete()
            Option.objects.bulk_create([Option(item=instance, **o) for o in options])
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


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'order', 'value')


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'content']


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
        if not (start_item_order := Question.objects.filter(item_id=attrs['start_item'].id).first().order) <= \
               (end_item_order := Question.objects.filter(item_id=attrs['end_item'].id).first().order):
            raise serializers.ValidationError('Start item must be before or equal to end item')

        # check if sections overlap
        sections = Section.objects.filter(start_item_id__in=Item.objects.filter(survey_id=survey_id))

        for section in sections:
            section.start_item_order = Question.objects.filter(item_id=section.start_item_id).first().order
            section.end_item_order = Question.objects.filter(item_id=section.end_item_id).first().order
            if section.start_item_order <= start_item_order <= section.end_item_order or \
               section.start_item_order <= end_item_order <= section.end_item_order:
                raise serializers.ValidationError('Sections overlap')

        return attrs

    def update(self, instance, validated_data):
        pass


class PreconditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precondition
        fields = ('expected_option', 'next_item')
