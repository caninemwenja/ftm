from django.db import models
from django.contrib.auth import get_user_model

from lib import utils


class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Question(TimestampedModel):
    owner = models.ForeignKey(get_user_model())
    text = models.TextField()
    published = models.BooleanField(default=False)

    def mark(self, stemmer, wsd, sim, scorer, tentative_threshold_opt, threshold_opt=None):
        results = []

        marking_answers = self.markinganswer_set.all()

        tentative_threshold = 0

        if tentative_threshold_opt == 'min':
            tentative_threshold = 10000

        thresholds = []

        for answer in marking_answers:
            result = utils.similarity(
                answer.text, answer.text,
                stemmer=stemmer, wsd=wsd, similarity=sim, scoring=scorer)

            if tentative_threshold_opt == 'min':
                if result['score'] < tentative_threshold:
                    tentative_threshold = result['score']

            if tentative_threshold_opt == 'mean':
                thresholds.append(result['score'])

            if tentative_threshold_opt == 'max':
                if result['score'] > tentative_threshold:
                    tentative_threshold = result['score']

        if tentative_threshold_opt == 'mean':
            tentative_threshold = sum(thresholds) / len(thresholds)

        threshold = threshold_opt if threshold_opt else tentative_threshold

        for answer in self.studentanswer_set.all():
            max_result = None
            max_score = -1
            max_markinganswer = None

            for marking_answer in marking_answers:
                context = self.text + " " + marking_answer.text
                result = utils.similarity(
                    marking_answer.text, answer.text,
                    stemmer=stemmer, wsd=wsd, similarity=sim, scoring=scorer, context=context)
                if result['score'] > max_score:
                    max_result = result
                    max_score = result['score']
                    max_markinganswer = marking_answer

            sent_1_terms = [candidate['word1']['token'] for candidate in max_result['candidates']]
            sent_2_terms = [candidate['word2']['token'] for candidate in max_result['candidates']]

            results.append(
                {'answer': answer,
                 'marking_answer': max_markinganswer,
                 'result': max_result,
                 'sent_1_terms': sent_1_terms,
                 'sent_2_terms': sent_2_terms})

        return results, threshold


class MarkingAnswer(TimestampedModel):
    question = models.ForeignKey(Question)
    text = models.TextField()


class StudentAnswer(TimestampedModel):
    question = models.ForeignKey(Question)
    text = models.TextField()
    student = models.ForeignKey(get_user_model())
