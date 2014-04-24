__author__ = 'caninemwenja'

from Levenshtein import distance

from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from munkres import Munkres, make_cost_matrix

from lesk import cosine_lesk, simple_lesk, adapted_lesk, original_lesk
from lib.similarity import sim, max_similarity


def tokenize(sentence, stemmer='lancaster'):
    tokens = sentence.split(" ")

    tokenized = []

    st = LancasterStemmer()

    if stemmer == "porter":
        st = PorterStemmer()

    # remove stop words
    for token in tokens:
        if token not in stopwords.words('english'):
            token = st.stem(token)
            tokenized.append(token)

    return tokenized


def wsd(context_sentence, word, option="adapted"):
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

            sim_score = similarity(sense, sense2, sim_option) or 0

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


def similarity(sense1, sense2, option="path"):
    if sense1 and sense2:
        return sim(sense1, sense2, option)

    return None
