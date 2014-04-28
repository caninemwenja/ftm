__author__ = 'caninemwenja'

from django.core.management import BaseCommand
from django.contrib.auth import get_user_model

from questions.models import Question

import sys
import glob
import random
import os


class Command(BaseCommand):

    def _parse(self, dirname, filename):
        pathname = os.path.join(dirname, filename)
        f = open(pathname)

        question = ""
        marking_scheme = []
        answers = []

        count = 0

        getting_answers = False

        for whole_line in f:
            line = whole_line[:-1]

            if count == 0:
                question = line
                count += 1
                continue

            if line == "----":
                getting_answers = True
                continue

            if not getting_answers:
                marking_scheme.append(line)
                continue

            splits = line.split("::", 2)
            answers.append((splits[0], bool(splits[1])))

        f.close()

        return question, marking_scheme, answers

    def _parameter_combos(self):
        stemmers = ('porter', 'lancaster', 'pattern')

        wsds = ('adapted', 'simple', 'original', 'cosine', 'wup')

        sims = ('path', 'wup', 'lch', 'res', 'jcn', 'lin')

        scorers = ('min', 'mean')

        thresholds = ('min', 'mean', 'max')

        combos = []

        for stem in stemmers:
            for w in wsds:
                for s in sims:
                    for sc in scorers:
                        for thresh in thresholds:
                            combo = {
                                'stemmer': stem,
                                'wsd': w,
                                'similarity': s,
                                'scorer': sc,
                                'tentative_threshold_opt': thresh
                            }
                            combos.append(combo)

        return combos

    def handle(self, *args, **options):
        if len(sys.argv) < 3:
            print "Usage: {0} {1} <test data folder>".format(sys.argv[0], sys.argv[1])
            return

        user_model = get_user_model()
        user = user_model(username="test_user"+str(int(random.random()*10000)))
        user.set_password("testing")
        user.save()

        test_data_folder = sys.argv[2]
        testing_answers = {}

        measures = {}

        combos = self._parameter_combos()

        for name in glob.glob1(test_data_folder, '*.question'):
            question, marking_scheme, answers = self._parse(test_data_folder, name)

            q = Question.objects.create(text=question, owner=user)

            for scheme in marking_scheme:
                q.markinganswer_set.create(text=scheme)

            for answer, correct in answers:
                ans = q.studentanswer_set.create(text=answer, student=user)
                testing_answers[str(q.id)+":"+str(ans.id)] = correct

            for combo in combos:
                measure = measures.setdefault(str(combo), {
                    'positives': 0,
                    'negatives': 0,
                    'false_positives': 0,
                    'false_negatives': 0,
                    'true_positives': 0,
                    'true_negatives': 0,
                })

                try:
                    results, threshold = q.mark(**combo)
                except IndexError:
                    continue

                #print results, threshold

                for result in results:

                    ref_id = str(q.id)+":"+str(result['answer'].id)
                    ans_correct = result['result']['score'] >= threshold

                    if ans_correct:
                        measure['positives'] += 1
                    else:
                        measure['negatives'] += 1

                    testing_answer = testing_answers[ref_id]

                    if ans_correct and testing_answer:
                        measure['true_positives'] += 1
                    elif ans_correct and not testing_answer:
                        measure['false_positives'] += 1
                    elif not ans_correct and not testing_answer:
                        measure['false_negatives'] += 1
                    else:
                        measure['true_negatives'] += 1

                    measures[str(combo)] = measure

            q.delete()

        user.delete()

        print 'stemmer, wsd, similarity, scorer, tentative_threshold, positives, ' \
              'negatives, true positives, false positives, true negatives, false negatives'

        for combo in combos:
            row = []

            row.append(combo['stemmer'])
            row.append(combo['wsd'])
            row.append(combo['similarity'])
            row.append(combo['scorer'])
            row.append(combo['tentative_threshold_opt'])
            row.append(str(measures[str(combo)]['positives']))
            row.append(str(measures[str(combo)]['negatives']))
            row.append(str(measures[str(combo)]['true_positives']))
            row.append(str(measures[str(combo)]['false_positives']))
            row.append(str(measures[str(combo)]['true_negatives']))
            row.append(str(measures[str(combo)]['false_negatives']))

            print ",".join(row)