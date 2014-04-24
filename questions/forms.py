__author__ = 'caninemwenja'

from django import forms
from .models import Question, MarkingAnswer, StudentAnswer


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', )


class MarkingAnswerForm(forms.ModelForm):
    class Meta:
        model = MarkingAnswer
        fields = ('text', )


class StudentAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ('text', )


class MarkingForm(forms.Form):
    stemmers = (
        ('porter', 'Porter Stemmer'),
        ('lancaster', 'Lancaster Stemmer')
    )

    wsds = (
        ('adapted', 'Adapted Lesk'),
        ('simple', 'Simple Lesk'),
        ('original', 'Original Lesk'),
        ('cosine', 'Cosine Lesk'),
        ('wup', 'Wu-palmer Similarity')
    )
    
    sims = (
        ('path', "Path Similarity"),
        ('wup', 'Wu-Palmer Similarity'),
        ('lch', 'Leacock-Chodorow Similarity'),
        ('res', 'Resnik Similarity'),
        ('jcn', 'Jiang-Conrath Similarity'),
        ('lin', 'Lin Similarity'),
    )

    scorers = (
        ('min', 'Minimum'),
        ('mean', 'Mean')
    )

    thresholds = (
        ('min', 'Minimum'),
        ('mean', 'Mean'),
        ('max', 'Maximum')
    )

    stemmer = forms.ChoiceField(choices=stemmers, required=True)
    wsd = forms.ChoiceField(choices=wsds, required=True)
    sim = forms.ChoiceField(choices=sims, required=True)
    scorer = forms.ChoiceField(choices=scorers, required=True)
    tentative_threshold = forms.ChoiceField(choices=thresholds, required=True)
    threshold = forms.FloatField(required=False)
