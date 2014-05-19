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
            if whole_line[-1] == '\n':
                line = whole_line[:-1]
            else:
                line = whole_line

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
            correct = False
            if splits[1] == 'True':
                correct = True

            print line, correct

            answers.append((splits[0], correct))

        f.close()

        return question, marking_scheme, answers

    def _parameter_combos(self):
        #stemmers = ('porter', 'lancaster', 'pattern')
        stemmers = ('porter', 'pattern')

        #wsds = ('adapted', 'simple', 'original', 'cosine', 'wup')
        wsds = ('adapted', )

        #sims = ('path', 'wup', 'lch', 'res', 'jcn', 'lin')
        sims = ('path', 'lin')

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
        if len(sys.argv) < 5:
            print "Usage: {} {} <test data folder> <raw csv> <summary csv>".format(
                sys.argv[0], sys.argv[1])
            return

        user_model = get_user_model()
        user = user_model(username="test_user"+str(int(random.random()*10000)))
        user.set_password("testing")
        user.save()

        test_data_folder = sys.argv[2]
        raw_csv_filename = sys.argv[3]
        summary_csv_filename = sys.argv[4]

        raw_csv_file = open(raw_csv_filename, "w")
        summary_csv_file = open(summary_csv_filename, "w")

        testing_answers = {}

        measures = {}

        combos = self._parameter_combos()

        headers = "Question;Answer;Stemmer;Wsd;Similarity;Scorer;" \
                  "TentativeThreshold;Score;Threshold;IsActuallyCorrect;IsCorrect;" \
                  "IsPositive;IsNegative;IsTruePositive;IsFalsePositive;IsTrueNegative;IsFalseNegative"

        print headers
        raw_csv_file.write(headers+"\n")

        for name in glob.glob1(test_data_folder, '*.question'):
            question, marking_scheme, answers = self._parse(test_data_folder, name)

            q = Question.objects.create(text=question, owner=user)

            for scheme in marking_scheme:
                q.markinganswer_set.create(text=scheme)

            for answer, correct in answers:
                ans = q.studentanswer_set.create(text=answer, student=user)
                # print ans, correct
                testing_answers[str(q.id)+":"+str(ans.id)] = correct

            for combo in combos:
                results, threshold = q.mark(**combo)

                for result in results:
                    measure = {
                        'positives': 0,
                        'negatives': 0,
                        'false_positives': 0,
                        'false_negatives': 0,
                        'true_positives': 0,
                        'true_negatives': 0,
                    }
                    measure2 = measures.setdefault(str(combo), {
                        'positives': 0,
                        'negatives': 0,
                        'false_positives': 0,
                        'false_negatives': 0,
                        'true_positives': 0,
                        'true_negatives': 0,
                    })

                    ref_id = str(q.id)+":"+str(result['answer'].id)
                    testing_answer = testing_answers[ref_id]

                    if not result['result']['score']:
                        result['result']['score'] = 0

                    if not threshold:
                        threshold = 0

                    ans_correct = float(result['result']['score']) >= float(threshold)

                    out = []

                    out.append(q.text)
                    out.append(result['answer'].text)

                    if ans_correct:
                        measure['positives'] = 1
                        measure2['positives'] += 1
                    else:
                        measure['negatives'] = 1
                        measure2['negatives'] += 1

                    if ans_correct and testing_answer:
                        measure['true_positives'] = 1
                        measure2['true_positives'] += 1
                    elif ans_correct and not testing_answer:
                        measure['false_positives'] = 1
                        measure2['false_positives'] += 1
                    elif not ans_correct and testing_answer:
                        measure['false_negatives'] = 1
                        measure2['false_negatives'] += 1
                    else:
                        measure['true_negatives'] = 1
                        measure2['true_negatives'] += 1

                    measures[str(combo)] = measure2

                    out.append(combo['stemmer'])
                    out.append(combo['wsd'])
                    out.append(combo['similarity'])
                    out.append(combo['scorer'])
                    out.append(combo['tentative_threshold_opt'])
                    out.append(str(result['result']['score']))
                    out.append(str(threshold))
                    out.append(str(testing_answer))
                    out.append(str(ans_correct))
                    out.append(str(measure['positives']))
                    out.append(str(measure['negatives']))
                    out.append(str(measure['true_positives']))
                    out.append(str(measure['false_positives']))
                    out.append(str(measure['true_negatives']))
                    out.append(str(measure['false_negatives']))

                    csv_line = ";".join(out)
                    print csv_line
                    raw_csv_file.write(csv_line+"\n")

            q.delete()

        user.delete()

        print

        summary_headers = 'stemmer;wsd;similarity;scorer;tentative threshold;' \
                          'positives;' \
                          'negatives;true positives;false positives;true negatives;false negatives;'

        print summary_headers
        summary_csv_file.write(summary_headers+"\n")

        for combo in combos:
            row = []

            row.append(combo['stemmer'])
            row.append(combo['wsd'])
            row.append(combo['similarity'])
            row.append(combo['scorer'])
            row.append(combo['tentative_threshold_opt'])
            # all_answers = len(testing_answers.keys())
            # positive_answers = len([testing_answers[key] for key in testing_answers.keys() if testing_answers[key]])
            # negative_answers = len([testing_answers[key] for key in testing_answers.keys() if not testing_answers[key]])
            # row.append(str(all_answers))
            # row.append(str(positive_answers))
            # row.append(str(negative_answers))
            row.append(str(measures[str(combo)]['positives']))
            row.append(str(measures[str(combo)]['negatives']))
            row.append(str(measures[str(combo)]['true_positives']))
            row.append(str(measures[str(combo)]['false_positives']))
            row.append(str(measures[str(combo)]['true_negatives']))
            row.append(str(measures[str(combo)]['false_negatives']))
            # row.append(str(all_answers-measures[str(combo)]['positives']-measures[str(combo)]['negatives']))
            # row.append(str(positive_answers-measures[str(combo)]['positives']))
            # row.append(str(negative_answers-measures[str(combo)]['negatives']))

            summary_csv_line = ";".join(row)
            print summary_csv_line
            summary_csv_file.write(summary_csv_line+"\n")

        raw_csv_file.close()
        summary_csv_file.close()

        print "\nDone"
