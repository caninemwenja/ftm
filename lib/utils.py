__author__ = 'caninemwenja'

from Levenshtein import distance

from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from munkres import Munkres, make_cost_matrix

from pattern.text.en import wordnet
from pattern.text.en import singularize
from pattern.text.en import conjugate

from lesk import cosine_lesk, simple_lesk, adapted_lesk, original_lesk
from lib.similarity import sim, max_similarity

import string


class PatternStemmer(object):

    def stem(self, word):
        token = singularize(word)

        conjugation = conjugate(token, 'inf')
        if conjugation:
            token = str(conjugation)

        return token


def remove_punctuation(sentence):
    for symbol in string.punctuation:
        sentence = sentence.replace(symbol, '')

    return sentence


def tokenize(sentence, stemmer='lancaster'):
    tokens = remove_punctuation(sentence).lower().split(" ")

    tokenized = []
    originals = []

    st = LancasterStemmer()

    if stemmer == "porter":
        st = PorterStemmer()
    if stemmer == "pattern":
        st = PatternStemmer()

    # remove stop words
    for token in tokens:
        if token not in stopwords.words('english'):
            originals.append(token)
            token = st.stem(token)
            tokenized.append(token)

    return tokenized, originals


def wsd(context_sentence, word, option="adapted"):
    # clean context sentence
    context_sentence = remove_punctuation(context_sentence)
    wsd_fn = adapted_lesk
    if option == "simple":
        wsd_fn = simple_lesk
    elif option == "cosine":
        wsd_fn = cosine_lesk
    elif option == "original":
        wsd_fn = original_lesk
    elif option == "wup":
        wsd_fn = max_similarity

    return wsd_fn(context_sentence, word)


def exaggerated_edit_distance(word, word2):
    dist = (distance(word, word2)+1)
    # return 1 / (math.e ** dist)
    return 1 / dist


def relative_matrix(senses_1, tokens_1, senses_2, tokens_2, sim_option="path"):
    relative_matrix = []

    row_count = 0
    col_count = 0

    for sense in senses_1:
        row = []
        for sense2 in senses_2:
            edit_dist = exaggerated_edit_distance(tokens_1[row_count], tokens_2[col_count])

            sim_score = sense_similarity(sense, sense2, sim_option) or 0

            val = sim_score

            if edit_dist > sim_score:
                val = edit_dist

            print tokens_1[row_count], tokens_2[col_count], val, sim_score, edit_dist

            row.append(val)
            col_count += 1

        row_count += 1
        col_count = 0
        relative_matrix.append(row)

    return relative_matrix


def maximum_weight_bipartite(matrix):
    cost_matrix = make_cost_matrix(matrix, lambda cost: 100000 - cost)

    m = Munkres()
    indices = m.compute(cost_matrix)

    return indices


def sense_similarity(sense1, sense2, option="path"):
    if sense1 and sense2:
        return sim(sense1, sense2, option)

    return None


def similarity(sentence1, sentence2, **kwargs):
    print kwargs

    stemmer = kwargs.get('stemmer', 'porter')

    wsd_ = kwargs.get('wsd', 'adapted')

    sim = kwargs.get('similarity', 'path')

    scoring = kwargs.get('scoring', 'min')

    context = kwargs.get('context', '')

    tokens_1, original_1 = tokenize(sentence1, stemmer)
    tokens_2, original_2 = tokenize(sentence2, stemmer)

    senses_1 = [wsd(sentence1+" "+context, token, wsd_) for token in tokens_1 if token and len(token) > 0]
    senses_2 = [wsd(sentence2+" "+context, token, wsd_) for token in tokens_2 if token and len(token) > 0]

    rel_mat = relative_matrix(senses_1, tokens_1, senses_2, tokens_2, sim)

    indices = maximum_weight_bipartite(rel_mat)

    candidates = []

    vals = []
    for row, col in indices:
        candidate = {}

        val = rel_mat[row][col]
        vals.append(val)

        candidate['match'] = val
        candidate['word1'] = {
            'token': original_1[row],
            'definition': senses_1[row].definition if hasattr(senses_1[row], 'definition') else None,
        }
        candidate['word2'] = {
            'token': original_2[col],
            'definition': senses_2[col].definition if hasattr(senses_2[col], 'definition') else None,
        }

        candidates.append(candidate)

    score = min(vals)

    if scoring == 'mean':
        score = 2*sum(vals)/(len(tokens_1)+len(tokens_2))

    result = {
        'score': score,
        'candidates': candidates,
        'tokens_1': tokens_1,
        'tokens_2': tokens_2,
        'senses_1': senses_1,
        'senses_2': senses_2,
        'rel_mat': rel_mat,
    }

    return result
