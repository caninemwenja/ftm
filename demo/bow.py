from __future__ import division

__author__ = 'caninemwenja'

from lib.utils import tokenize, wsd, maximum_weight_bipartite, relative_matrix

import sys


def process(sentence, lesk_type="adapted", stemmer="lancaster"):
    tokens = tokenize(sentence, stemmer)

    senses = []

    for token in tokens:
        if token and len(token) > 0:
            ws = wsd(sentence, token, lesk_type)
            senses.append(ws)

    return senses, tokens


def similar(sentence_1, sentence_2, lesk_type="adapted", stemmer="lancaster", sim_option="path"):
    senses_1, tokens_1 = process(sentence_1, lesk_type, stemmer)
    senses_2, tokens_2 = process(sentence_2, lesk_type, stemmer)

    rel_mat = relative_matrix(senses_1, tokens_1, senses_2, tokens_2, sim_option)

    indices = maximum_weight_bipartite(rel_mat)

    candidates = []

    total = 0
    vals = []
    for row, col in indices:
        val = rel_mat[row][col]
        vals.append(val)
        candidates.append(
            (val,
             tokens_1[row],
             senses_1[row].definition if hasattr(senses_1[row], "definition") else senses_1[row],
             tokens_2[col],
             senses_2[col].definition if hasattr(senses_2[col], "definition") else senses_2[col],)
        )
        total += val

    total = min(vals)

    #return total / (len(tokens_1)+len(tokens_2)), candidates
    return total, candidates


def print_synset(synset):
    if synset:
        print synset, synset.definition


def print_all_synsets(synset_list):
    for synset in synset_list:
        print_synset(synset)


def my_print_matrix(matrix):
    for row in matrix:
        for cell in row:
            print cell, "\t",
        print


def main():
    if len(sys.argv) < 3:
        print "Usage: {0} sentence_1 sentence_2".format(sys.argv[0])
        return

    sentence_1 = sys.argv[1]
    sentence_2 = sys.argv[2]

    lesk_type = "adapted"

    if len(sys.argv) == 4:
        lesk_type = sys.argv[3]
    
    stemmer = "lancaster"

    if len(sys.argv) == 5:
        stemmer = sys.argv[4]

    sim_option = "path"

    if len(sys.argv) == 6:
        sim_option = sys.argv[5]

    score, candidates = similar(sentence_1, sentence_2, lesk_type, stemmer, sim_option)

    print "Score: ", score

    print "Reason:"
    for candidate in candidates:
        for elem in candidate:
            print repr(elem)+",",
        print

if __name__ == "__main__":
    main()
