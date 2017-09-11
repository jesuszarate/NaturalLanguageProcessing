#!/usr/bin/python
from math import log
import sys, getopt


def get_unigrams(filename):
    return list(unigram_freq(filename).keys())


def unigram_freq(filename):
    unigrams = {}
    with open(filename, 'r') as file:
        for line in file:
            tokens = line.split()
            for token in tokens:
                token = str.lower(token)
                if token not in unigrams:
                    unigrams[token] = 0
                unigrams[token] += 1
    return unigrams


def bigram_freq(filename):
    bigrams = {}
    with open(filename, 'r') as file:

        for line in file:
            tokens = line.split()
            prev = 'phi'
            for token in tokens:
                biToken = str.lower(prev + " " + token)
                if biToken not in bigrams:
                    bigrams[biToken] = 0
                bigrams[biToken] += 1
                prev = token
    return bigrams


def get_sum(frequencies):
    s = 0
    for k, v in frequencies.items():
        s += v
    return s
    #return sum(val for val in frequencies.values())


def compute_prob(frequencies):
    # frequencies = bigram_freq(filename)
    #N = get_sum(unigram_freq('../train.txt'))
    N = get_sum(frequencies)
    probs = {}
    for freq in frequencies:
        probs[freq] = frequencies[freq] / len(frequencies)#N
    return probs

# def compute_prob(frequencies):
#     # frequencies = bigram_freq(filename)
#     #N = get_sum(unigram_freq('../train.txt'))
#     N = get_sum(frequencies)
#     probs = {}
#     for freq in frequencies:
#         probs[freq] = frequencies[freq] / N
#     return probs

def compute_prob_smooth(frequencies):
    N = get_sum(frequencies)
    smoothing_val = N / (N + len(frequencies))
    for freq in frequencies:
        frequencies[freq] = (frequencies[freq] + 1) * smoothing_val
    return frequencies


def get_log_probability(test_data, probs):
    """
    Check to make sure that the log_2 (prob) is working
    :param test_data:
    :param probs:
    :return:
    """
    #if test_data[0] not in probs:
    #    return 'undefined'

    prod = 0#log(probs[test_data[0]], 2)
    for token in test_data:
        if token in probs:
            prod += log(probs[token], 2)
        else:
            return 'undefined'
    return prod


def print_probs(sentence, unigrams, bigrams, smooth_bigrams):
    print('S =', sentence)
    print('Unsmoothed Unigrams, logprob(S) =', round(unigrams, 4))
    print('Unsmoothed Bigrams, logprob(S) = ', bigrams if bigrams == 'undefined' else round(bigrams, 4))
    print('Smoothed Bigrams, logprob(S) = ', smooth_bigrams if smooth_bigrams == 'undefined' else round(smooth_bigrams, 4), "\n")


def get_sentence_unigram(line):
    return line.lower().split()


def get_sentence_bigram(line):
    bigrams = []
    prev = 'phi'
    tokens = line.split()
    for token in tokens:
        biToken = str.lower(prev + " " + token)
        bigrams.append(biToken)
        prev = token
    return bigrams


def get_unigram_prob(filename):
    return compute_prob(unigram_freq(filename))


def get_bigram_prob(filename):
    return compute_prob(bigram_freq(filename))

def get_bigram_smooth_prob(filename):
    return compute_prob_smooth(bigram_freq(filename))

def main(argv):
    training_file = ''
    test_file = ''
    seed_file = ''

    if not len(argv) == 3:
        print('ngrams.py <training_file> -test <test_file>')
        sys.exit(2)

    training_file = argv[0]
    unigram_training_prob = get_unigram_prob(training_file)  # compute_prob(unigram_freq(training_file))

    bigram_training_prob = get_bigram_prob(training_file)

    bigram_smooth_training_prob = get_bigram_smooth_prob(training_file)

    if argv[1] == '-test':
        test_file = argv[2]

        with open(test_file, 'r') as file:
            for line in file:
                unigram_p = get_log_probability(get_sentence_unigram(line), unigram_training_prob)
                sb = get_sentence_bigram(line)

                bigram_p = get_log_probability(get_sentence_bigram(line), bigram_training_prob)
                bigram_ps = get_log_probability(get_sentence_bigram(line), bigram_smooth_training_prob)

                print_probs(line, unigram_p, bigram_p, bigram_ps)

    elif argv[1] == '-gen':
        seed_file = argv[2]
        print('In gen')


if __name__ == "__main__":
    main(sys.argv[1:])
