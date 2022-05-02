# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Answers(models.Model):
    id = models.UUIDField(primary_key=True)
    question = models.ForeignKey('Questions', models.DO_NOTHING)
    content_numeric = models.IntegerField(blank=True, null=True)
    content_character = models.TextField(blank=True, null=True)
    option = models.ForeignKey('Options', models.DO_NOTHING, blank=True, null=True)
    submission = models.ForeignKey('SurveySubmissions', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'answers'


class Creators(models.Model):
    id = models.UUIDField(primary_key=True)
    email = models.CharField(max_length=320)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=18, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'creators'


class CreatorsInterviewees(models.Model):
    creator = models.ForeignKey(Creators, models.DO_NOTHING)
    interviewee = models.ForeignKey('Interviewees', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'creators_interviewees'


class Interviewees(models.Model):
    id = models.UUIDField(primary_key=True)
    email = models.CharField(max_length=320)
    first_name = models.CharField(max_length=63, blank=True, null=True)
    last_name = models.CharField(max_length=63, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'interviewees'


class Items(models.Model):
    id = models.UUIDField(primary_key=True)
    survey_id = models.UUIDField()
    section = models.ForeignKey('Sections', models.DO_NOTHING, blank=True, null=True)
    header = models.CharField(max_length=255, blank=True, null=True)
    type = models.SmallIntegerField(blank=True, null=True)
    required = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'items'


class Options(models.Model):
    id = models.UUIDField(primary_key=True)
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'options'


class OptionsItems(models.Model):
    option = models.ForeignKey(Options, models.DO_NOTHING)
    item = models.ForeignKey(Items, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'options_items'


# class Preconditions(models.Model):
#     id = models.UUIDField(primary_key=True)
#     item = models.ForeignKey(Items, models.DO_NOTHING)
#     expected_option = models.ForeignKey(Options, models.DO_NOTHING)
#     next_item = models.ForeignKey(Items, models.DO_NOTHING)
#
#     class Meta:
#         managed = False
#         db_table = 'preconditions'


class Questions(models.Model):
    id = models.UUIDField(primary_key=True)
    order = models.IntegerField()
    item = models.ForeignKey(Items, models.DO_NOTHING)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'questions'


class Sections(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sections'


class SurveySent(models.Model):
    id = models.UUIDField(primary_key=True)
    survey = models.ForeignKey('Surveys', models.DO_NOTHING)
    interviewee_id = models.UUIDField()

    class Meta:
        managed = False
        db_table = 'survey_sent'


class SurveySubmissions(models.Model):
    id = models.UUIDField(primary_key=True)
    submitted_at = models.DateTimeField()
    survey = models.ForeignKey('Surveys', models.DO_NOTHING)
    interviewee = models.ForeignKey(Interviewees, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'survey_submissions'


class Surveys(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(Creators, models.DO_NOTHING)
    created_at = models.DateTimeField()
    starts_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    paused = models.BooleanField()
    anonymous = models.BooleanField()
    greeting = models.TextField(blank=True, null=True)
    farewell = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'surveys'


class SurveysItems(models.Model):
    survey = models.ForeignKey(Surveys, models.DO_NOTHING)
    item = models.ForeignKey(Items, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'surveys_items'
