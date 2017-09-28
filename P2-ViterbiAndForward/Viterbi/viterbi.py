#!/usr/bin/python
from math import log
import sys, getopt
import numpy as np
from pathlib import Path


class viterbi():
    def __init__(self, transitionPr, emissionPr, tags, words):
        self.default_val = 0.0001
        self.words = words
        self.tags = tags

        self.W = len(self.words)
        self.T = len(self.tags)

        self.transitionPr = transitionPr
        self.emissionPr = emissionPr
        self.Scores = dict()
        self.BackPtr = dict()

    def compute(self):

        for t in range(0, self.T):
            word = self.transitionProb(self.words[0], self.tags[t])
            tag = self.emissionProb(self.tags[t], 'phi')
            self.Scores[(self.tags[t], self.words[0])] = word * tag
        self.BackPtr[(self.tags[self.T - 1], self.words[0])] = 0

        for w in range(1, self.W):
            for t in range(0, self.T):
                k, max_k = self.getMax(self.words[w - 1], self.tags[t])

                self.Scores[(self.tags[t], self.words[w])] = self.transitionProb(self.words[w], self.tags[t]) * max_k
                self.BackPtr[(self.tags[t], self.words[w])] = k

        return self.Scores

    def computeSeq(self):
        # print self.Scores
        Seq = []#[0] * len(self.BackPtr)
        #best_tag, Seq[self.words[self.W - 1]] = self.getMax_t(self.words[self.W - 1])
        best_tag, max_t = self.getMax_t(self.words[self.W - 1])
        Seq.append((self.words[self.W-1], max_t))
        pos = 0
        for w in xrange(self.W - 1, 0, -1):
            #Seq[self.words[w-1]] = self.getBackPointer(Seq, w)
            Seq.append((self.words[w-1], self.getBackPointer(Seq[pos], w)))
            pos+=1

        return log(best_tag, 2), Seq

    def getBackPointer(self, prvSeq, w):
        ptr = self.BackPtr[(prvSeq[1],self.words[w])]
        return self.tags[ptr]

    def getMax_t(self, W):
        mx = -float('infinity')
        max_t = -float('infinity')
        for t in range(self.T):
            tmp = self.getScore(self.tags[t], W)
            if mx < tmp:
                mx = tmp
                max_t = t
        return mx, self.tags[max_t]

    def getMax(self, word, tag_t):
        mx = -float("infinity")
        mx_k = 0
        for k in range(0, self.T):
            prevScore = self.getScore(self.tags[k], word)
            prevEm = self.emissionProb(tag_t, self.tags[k])
            tmp = prevScore * prevEm
            if tmp > mx:
                mx = tmp
                mx_k = k
        return mx_k, mx

    def getScore(self, item1, item2):
        if (item1, item2) in self.Scores:
            return self.Scores[(item1, item2)]
        return self.default_val

    def transitionProb(self, word, tag):
        if (word, tag) in self.transitionPr:
            return self.transitionPr[(word, tag)]
        return self.default_val

    def emissionProb(self, tag1, tag2):
        if (tag1, tag2) in self.emissionPr:
            return self.emissionPr[tag1, tag2]
        return self.default_val


class forward():
    def __init__(self, transitionPr, emissionPr, tags, words):
        self.default_val = 0.0001

        self.words = words
        self.tags = tags

        self.W = len(self.words)
        self.T = len(self.tags)

        self.transitionPr = transitionPr
        self.emissionPr = emissionPr

        self.seqSum = dict()

        for t in range(0, self.T):
            self.seqSum[(self.tags[t], self.words[0])] = \
                self.transitionProb(self.words[0], self.tags[t]) * self.emissionProb(self.tags[t], 'phi')

    def computeForwardProbs(self):

        for w in range(1, self.W):
            for t in range(0, self.T):
                self.seqSum[(self.tags[t], self.words[w])] = self.transitionProb(self.words[w], self.tags[t]) * \
                                                             self.getProbSum(self.words[w - 1], self.tags[t])

    def computeLexicalProbs(self):

        probs = dict()
        for w in range(0, self.W):
            for t in range(0, self.T):
                Sum = self.getSum(w)
                Sum = Sum if Sum != 0 else self.default_val
                # if Sum != 0:
                probs[(self.words[w], self.tags[t])] = round(self.getSeqSum(self.tags[t], self.words[w]) / Sum, 4)
                # else:
                #    probs[(self.words[w], self.tags[t])] = 0
        return probs

    def getSum(self, w):
        Sum = 0
        for j in range(0, self.T):
            Sum += self.getSeqSum(self.tags[j], self.words[w])
        return Sum

    def transitionProb(self, word, tag):
        if (word, tag) in self.transitionPr:
            return self.transitionPr[(word, tag)]
        return self.default_val

    def emissionProb(self, tag1, tag2):
        if (tag1, tag2) in self.emissionPr:
            return self.emissionPr[tag1, tag2]
        return self.default_val

    def getProbSum(self, word, tag_t):
        Sum = 0
        for j in range(0, self.T):
            Sum += self.getSeqSum(self.tags[j], word) * self.emissionProb(tag_t, self.tags[j])
        return Sum

    def getSeqSum(self, tag, word):
        if (tag, word) in self.seqSum:
            return self.seqSum[(tag, word)]
        return self.default_val


def readProbs(probabilities_file, tags):
    transitions = dict()
    emmissions = dict()
    with open(probabilities_file, 'r') as file:
        for line in file:
            lineSplit = line.split()
            if lineSplit[1] and lineSplit[0] in tags:
                emmissions[(lineSplit[0], lineSplit[1])] = float(lineSplit[2])
            else:
                transitions[(lineSplit[0], lineSplit[1])] = float(lineSplit[2])
    return transitions, emmissions


def readSentence(file_name):
    lines = []
    with open(file_name, 'r') as file:
        for line in file:
            lines.append(line)
    return lines


def does_file_exist(filename):
    file = Path(filename)
    if file.is_file():
        return True
    return False


def genereate_trace_file(type, data, extension='trace'):
    with open('ngrams{0}.{1}'.format(type, extension), 'w') as of:
        for line in data:
            of.write(line + '\n')


# def print_results():

def main(argv):
    if not len(argv) == 2:
        print('python viterbi.py <probabilities file> <sentences file>')
        sys.exit(2)

    if not does_file_exist(argv[0]):
        print('In argument 1 file does not exist: {0}'.format(argv[0]))
        sys.exit(2)
    elif not does_file_exist(argv[1]):
        print('In argument 2 file does not exist: {0}'.format(argv[1]))
        sys.exit(2)

    probabilities_file = argv[0]

    sentence_file = argv[1]

    lines = readSentence(sentence_file)
    # sentence

    tags = ['noun', 'verb', 'inf', 'prep', 'phi']
    for sentence in lines:
        words = sentence.strip().split()
        probs = readProbs(probabilities_file, tags)

        vit = viterbi(probs[0], probs[1], tags, words)
        scores = vit.compute()
        best_tag, seq = vit.computeSeq()

        print ("PROCESSING SENTENCE: {0}".format(sentence))

        p_tags = ['noun', 'verb', 'inf', 'prep']

        print ('FINAL VITERBI NETWORK')
        for w in words:
            for t in p_tags:
                v = scores[(t, w)]
                val = 0 if v == 0 else round(log(v, 2), 4)
                print("P({0}={1}) = {2:.4f}".format(w, t, val))
        # print('\n')
        print

        print ('FINAL BACKPTR NETWORK')

        for w in words:
            for t in p_tags:
                if (t, w) in vit.BackPtr:
                    val = vit.tags[vit.BackPtr[(t, w)]]
                    #val = 0 if v == 0 else round(log(v, 2), 4)
                    print("P({0}={1}) = {2}".format(w, t, val))
        print

        print ('BEST TAG SEQUENCE HAS LOG PROBABILITY = {0:.4f}'.format(best_tag))
        # for w in words:
        #     for t in p_tags:
        for val in seq:
                print ('{0}->{1}'.format(val[0], val[1]))
        print

        print ('FORWARD ALGORITHM RESULTS')
        f_alg = forward(probs[0], probs[1], tags, words)
        f_alg.computeForwardProbs()
        ps = f_alg.computeLexicalProbs()

        for w in words:
            for t in p_tags:
                print('P({0}={1}) = {2:.4f}'.format(w, t, ps[(w, t)]))

        # print('\n')
        print


if __name__ == "__main__":
    main(sys.argv[1:])
