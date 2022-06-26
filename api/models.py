from django.db import models
import uuid


class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey('Item', related_name='options', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'options'


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_item = models.ForeignKey('Item', related_name='start_item', on_delete=models.CASCADE)
    end_item = models.ForeignKey('Item', related_name='end_item', on_delete=models.CASCADE)

    class Meta:
        db_table = 'sections'

    def get_items_in_order(self):
        items = Item.objects.prefetch_related('questions').filter(section=self)
        return sorted(items, key=lambda x: x.get_first_question_order())

    def get_start_question_order(self):
        return self.start_item.get_first_question_order()

    def get_survey_id(self):
        return self.start_item.survey_id


class Creator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=320, unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=18, blank=True, null=True)

    class Meta:
        db_table = 'creators'


class Survey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator_id = models.ForeignKey(Creator, models.CASCADE, db_column='creator_id')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    starts_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    paused = models.BooleanField()
    anonymous = models.BooleanField()
    greeting = models.TextField(blank=True, null=True)
    farewell = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'surveys'

    def get_sections_in_order(self):
        items = Item.objects.prefetch_related('questions',  'options').filter(survey=self).values_list('id')
        sections = Section.objects.select_related('start_item', 'end_item').filter(start_item_id__in=items).order_by()
        return sorted(sections, key=lambda x: x.get_start_question_order())

    def get_items_in_order(self):
        items = Item.objects.prefetch_related('questions', 'options').filter(survey=self)
        return sorted(items, key=lambda x: x.get_first_question_order())

    def get_items(self):
        return Item.objects.filter(survey=self)


class Item(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    survey = models.ForeignKey(Survey, related_name='items', on_delete=models.CASCADE, db_column='survey_id')
    type = models.SmallIntegerField(blank=True, null=True)
    required = models.BooleanField()

    class Meta:
        db_table = 'items'

    def get_first_question_order(self):
        if not Question.objects.filter(item=self):
            raise AttributeError('Item exists without any question')
        return Question.objects.filter(item=self).order_by('order').first().order

    def is_before(self, item: 'Item'):
        return Question.objects.filter(item__in=[self, item]).order_by('order').first().item_id == self.id


class Question(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    order = models.IntegerField()
    item = models.ForeignKey(Item, related_name='questions', on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        db_table = 'questions'

    def get_item_type(self):
        return self.item.type


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    question = models.ForeignKey(Question, models.CASCADE)
    content_numeric = models.IntegerField(blank=True, null=True)
    content_character = models.TextField(blank=True, null=True)
    option = models.ForeignKey(Option, on_delete=models.DO_NOTHING, blank=True, null=True)
    submission = models.ForeignKey('Submission', models.CASCADE)

    class Meta:
        db_table = 'answers'


class Interviewee(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.CharField(max_length=320)
    first_name = models.CharField(max_length=63, blank=True, null=True)
    last_name = models.CharField(max_length=63, blank=True, null=True)

    class Meta:
        db_table = 'interviewees'


class SurveySent(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    survey = models.ForeignKey(Survey, models.DO_NOTHING)
    interviewee_id = models.UUIDField()

    class Meta:
        db_table = 'survey_sent'


class Precondition(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    item = models.ForeignKey('Item', models.CASCADE, related_name='preconditions')
    expected_option = models.ForeignKey(Option, models.DO_NOTHING)
    next_item = models.ForeignKey('Item', models.DO_NOTHING, related_name='preconditions_next')

    class Meta:
        db_table = 'preconditions'


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    submitted_at = models.DateTimeField(auto_now_add=True)
    survey = models.ForeignKey('Survey', models.DO_NOTHING)
    interviewee = models.ForeignKey('Interviewee', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'submissions'
