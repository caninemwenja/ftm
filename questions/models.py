from django.db import models
from django.contrib.auth import get_user_model


class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Question(TimestampedModel):
    owner = models.ForeignKey(get_user_model())
    text = models.TextField()
    published = models.BooleanField(default=False)


class MarkingAnswer(TimestampedModel):
    question = models.ForeignKey(Question)
    text = models.TextField()


class StudentAnswer(TimestampedModel):
    question = models.ForeignKey(Question)
    text = models.TextField()
    student = models.ForeignKey(get_user_model())
