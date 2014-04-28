from __future__ import division

__author__ = 'caninemwenja'

from lib.utils import similarity

import sys


def main():
    if len(sys.argv) < 3:
        print "Usage: {0} sentence_1 sentence_2 wsd stemmer sim scoring context".format(sys.argv[0])
        return

    sentence_1 = sys.argv[1]
    sentence_2 = sys.argv[2]

    lesk_type = "adapted"

    if len(sys.argv) >= 4:
        lesk_type = sys.argv[3]
    
    stemmer = "lancaster"

    if len(sys.argv) >= 5:
        stemmer = sys.argv[4]

    sim_option = "path"

    if len(sys.argv) >= 6:
        sim_option = sys.argv[5]

    scoring_option = "min"

    if len(sys.argv) >= 7:
        scoring_option = sys.argv[6]

    context = ""

    if len(sys.argv) >= 8:
        context = sys.argv[7]

    result = similarity(
        sentence_1, sentence_2,
        wsd=lesk_type, stemmer=stemmer,
        similarity=sim_option, scoring=scoring_option, context=context)

    print "Score: ", result['score']

    print "Reason:"
    for candidate in result['candidates']:
        print candidate['word1']['token'], \
            "("+str(candidate['word1']['definition'])+")",\
            candidate['match'], \
            candidate['word2']['token'], \
            "("+str(candidate['word2']['definition'])+")"

if __name__ == "__main__":
    main()
