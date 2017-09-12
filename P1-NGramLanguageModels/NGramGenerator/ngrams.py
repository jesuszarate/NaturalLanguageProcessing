#!/usr/bin/python
from math import log
import sys, getopt


class ngrams():
    unigrams = {}

    def __init__(self, filename):
        self.unigrams = self.unigram_freq(filename)

    def get_unigrams(self, filename):
        return list(self.unigram_freq(filename).keys())

    def unigram_freq(self, filename):
        unigrams = {}
        phi = 0
        with open(filename, 'r') as file:
            for line in file:
                phi += 1
                tokens = line.split()
                for token in tokens:
                    token = str.lower(token)
                    if token not in unigrams:
                        unigrams[token] = 0
                    unigrams[token] += 1
        unigrams['phi'] = phi
        return unigrams

    def bigram_freq(self, filename):
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

    def get_sum(self, frequencies):
        # s = 0
        # for k, v in frequencies.items():
        #     s += v
        # return s

        s = sum(val for val in frequencies.values())
        return s

    def compute_prob(self, frequencies):
        N = self.get_sum(frequencies)
        probs = {}
        for bigram, freq in frequencies.items():
            b = bigram.split()
            probs[bigram] = log((freq / N), 2)
        return probs

    def compute_prob_bigrams(self, frequencies):
        # frequencies = bigram_freq(filename)
        # N = get_sum(unigram_freq('../train.txt'))
        N = self.get_sum(frequencies)
        probs = {}
        for bigram, freq in frequencies.items():
            word = bigram.split()[0]
            N = self.unigrams[word]
            probs[bigram] = log((freq / N), 2)
        return probs

    def compute_prob_smooth(self, frequencies):
        N = self.get_sum(frequencies)
        smoothing_val = N / (N + len(frequencies))
        for freq in frequencies:
            frequencies[freq] = (frequencies[freq] + 1) * smoothing_val
        return frequencies

    def get_unigram_count(self, filename):
        count = 0
        with open(filename, 'r') as file:
            for line in file:
                count += len(line.split())
        return count

    def get_log_probability(self, test_data, probs):
        """
        Check to make sure that the log_2 (prob) is working
        :param test_data:
        :param probs:
        :return:
        """
        prod = 0
        for token in test_data:
            if token in probs:
                prod += probs[token]
            else:
                return 'undefined'
        return prod

    def print_probs(self, sentence, unigrams, bigrams, smooth_bigrams):
        print('S =', sentence)
        print('Unsmoothed Unigrams, logprob(S) =', round(unigrams, 4))
        print('Unsmoothed Bigrams, logprob(S) = ', bigrams if bigrams == 'undefined' else round(bigrams, 4))
        print('Smoothed Bigrams, logprob(S) = ',
              smooth_bigrams if smooth_bigrams == 'undefined' else round(smooth_bigrams, 4), "\n")

    def get_sentence_unigram(self, line):
        return line.lower().split()

    def get_sentence_bigram(self, line):
        bigrams = []
        prev = 'phi'
        tokens = line.split()
        for token in tokens:
            biToken = str.lower(prev + " " + token)
            bigrams.append(biToken)
            prev = token
        return bigrams

    def get_unigram_prob(self, filename):
        return self.compute_prob(self.unigrams)

    def get_bigram_prob(self, filename):
        return self.compute_prob_bigrams(self.bigram_freq(filename))

    def get_bigram_smooth_prob(self, filename):
        return self.compute_prob_smooth(self.bigram_freq(filename))


def main(argv):
    training_file = ''
    test_file = ''
    seed_file = ''
    ng = None

    if not len(argv) == 3:
        print('ngrams.py <training_file> -test <test_file>')
        sys.exit(2)

    training_file = argv[0]

    ng = ngrams(training_file)

    unigram_training_prob = ng.get_unigram_prob(training_file)  # compute_prob(unigram_freq(training_file))

    bigram_training_prob = ng.get_bigram_prob(training_file)

    bigram_smooth_training_prob = ng.get_bigram_smooth_prob(training_file)

    if argv[1] == '-test':
        test_file = argv[2]

        with open(test_file, 'r') as file:
            for line in file:
                unigram_p = ng.get_log_probability(ng.get_sentence_unigram(line), unigram_training_prob)
                sb = ng.get_sentence_bigram(line)

                bigram_p = ng.get_log_probability(ng.get_sentence_bigram(line), bigram_training_prob)
                bigram_ps = ng.get_log_probability(ng.get_sentence_bigram(line), bigram_smooth_training_prob)

                ng.print_probs(line, unigram_p, bigram_p, bigram_ps)

    elif argv[1] == '-gen':
        seed_file = argv[2]
        print('In gen')


if __name__ == "__main__":
    main(sys.argv[1:])
