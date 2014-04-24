__author__ = 'caninemwenja'

from django.forms import ModelForm
from .models import Question, MarkingAnswer


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ('text', )


class MarkingAnswerForm(ModelForm):
    class Meta:
        model = MarkingAnswer
        fields = ('text', )
