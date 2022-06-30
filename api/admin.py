from django.contrib import admin
from .models import Survey, Item, Section, Question, Answer, Option, Submission, Creator, Interviewee

# Register your models here.
admin.site.register(Survey)
admin.site.register(Item)
admin.site.register(Section)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Option)
admin.site.register(Submission)
admin.site.register(Creator)
admin.site.register(Interviewee)