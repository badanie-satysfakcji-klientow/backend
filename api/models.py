# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import uuid


class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey('Item', related_name='options', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'options'


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sections'


class Creator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=320, unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=18, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'creators'


class Survey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator_id = models.ForeignKey(Creator, models.DO_NOTHING, db_column='creator_id')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    starts_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    paused = models.BooleanField()
    anonymous = models.BooleanField()
    greeting = models.TextField(blank=True, null=True)
    farewell = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'surveys'


class Item(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    survey = models.ForeignKey(Survey, on_delete=models.DO_NOTHING, db_column='survey_id')
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING)
    header = models.CharField(max_length=255, blank=True, null=True)
    type = models.SmallIntegerField(blank=True, null=True)
    required = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'items'


class Question(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    order = models.IntegerField()
    item = models.ForeignKey(Item, related_name='questions', on_delete=models.DO_NOTHING)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'questions'


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    question = models.ForeignKey(Question, models.DO_NOTHING)
    content_numeric = models.IntegerField(blank=True, null=True)
    content_character = models.TextField(blank=True, null=True)
    option = models.ForeignKey(Option, models.DO_NOTHING, blank=True, null=True)
    # submission = models.ForeignKey('SurveySubmission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'answers'


# class CreatorsInterviewees(models.Model):
#     creator = models.ForeignKey(Creators, models.DO_NOTHING)
#     interviewee = models.ForeignKey('Interviewees', models.DO_NOTHING)
#
#     class Meta:
#         managed = False
#         db_table = 'creators_interviewees'


class Interviewee(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.CharField(max_length=320)
    first_name = models.CharField(max_length=63, blank=True, null=True)
    last_name = models.CharField(max_length=63, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'interviewees'


class SurveySent(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    survey = models.ForeignKey(Survey, models.DO_NOTHING)
    interviewee_id = models.UUIDField()

    class Meta:
        managed = False
        db_table = 'survey_sent'


class Precondition(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    item = models.ForeignKey('Item', models.DO_NOTHING, related_name='preconditions')
    expected_option = models.ForeignKey(Option, models.DO_NOTHING)
    next_item = models.ForeignKey('Item', models.DO_NOTHING, related_name='preconditions_next')

    class Meta:
        managed = False
        db_table = 'preconditions'


class SurveySubmission(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    submitted_at = models.DateTimeField()
    survey = models.ForeignKey(Survey, models.DO_NOTHING)
    interviewee = models.ForeignKey(Interviewee, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'survey_submissions'