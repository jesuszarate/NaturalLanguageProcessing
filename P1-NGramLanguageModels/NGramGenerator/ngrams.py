#!/usr/bin/python
from math import log
import sys, getopt
import numpy as np
import random


class ngrams():
    def __init__(self, filename):
        self.unigrams, self.fileSize = self.unigram_freq(filename)
        self.bigrams, self.B_seed = self.bigram_freq(filename)

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
        return unigrams, phi

    def bigram_freq(self, filename):
        bigrams = {}
        b_seed = {}
        with open(filename, 'r') as file:
            for line in file:
                tokens = line.split()
                prev = 'phi'
                for token in tokens:
                    biToken = str.lower(prev + " " + token)
                    token = token.lower()

                    if prev not in b_seed:
                        b_seed[prev] = set()

                    if biToken not in bigrams:
                        bigrams[biToken] = 0

                    b_seed[prev].add(token)
                    bigrams[biToken] += 1
                    prev = token
        bigrams['phi'] = self.fileSize
        return bigrams, b_seed

    def get_sum(self, frequencies):
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
        probs = {}
        for bigram, freq in frequencies.items():
            word = bigram.split()[0]
            N = self.unigrams[word] if word != 'phi' else self.fileSize
            probs[bigram] = log((freq / N), 2)
        return probs

    def compute_prob_smooth(self, frequencies):
        V = len(self.unigrams)
        probs = {}
        for bigram, freq in frequencies.items():
            word = bigram.split()[0]
            N = self.unigrams[word] if word != 'phi' else self.fileSize
            probs[bigram] = log(((freq + 1) / (N + V)), 2)
        return probs

    def get_unigram_count(self, filename):
        count = 0
        with open(filename, 'r') as file:
            for line in file:
                count += len(line.split())
        return count

    def get_smooth_sentence_probability(self, test_data, probs):
        prod = 0
        V = len(self.unigrams)
        for token in test_data:
            prev = token.split()[0]
            if token in probs:
                prod += probs[token]
            else:
                N = self.unigrams[prev] if prev != 'phi' else self.fileSize
                prod += log(((1) / (N + V)), 2)
        return prod

    def get_probability(self, test_data, probs):
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

    def print_gen_sentences(self, seed, sentences):
        print('Seed = {0}\n'.format(seed))

        for i, sentence in enumerate(sentences):
                print('Sentence {0}: {1}'.format(i+1, sentence))
        print()

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

    def read_seed_file(self, filename):
        seeds = []
        with open(filename, 'r') as file:
            for line in file:
                seeds.append(line.strip())
        return seeds

    def get_unigram_prob(self, filename):
        return self.compute_prob(self.unigrams)

    def get_bigram_prob(self, filename):
        return self.compute_prob_bigrams(self.bigram_freq(filename)[0])

    def get_bigram_smooth_prob(self, filename):
        return self.compute_prob_smooth(self.bigram_freq(filename)[0])

    def get_B_seed(self, seed):
        for s in self.B_seed:
            if s in self.bigrams:
                print()

    def generate_sentence(self, seed):
        sentence = seed
        seed = seed.lower()
        last = seed
        for i in range(10):
            if last == '.' or last == '?' or last == '!':
                break
            follow_words = []
            frequencies = []
            size = 0
            for s2 in self.B_seed[seed]:
                bg = self.concat_strings(seed, s2)
                follow_words.append(s2)
                freq = self.bigrams[bg]
                frequencies.append(freq)
                size += freq
            # Compute the probability by dividing each value by the size
            probabilities = list(map(lambda x: x / size, frequencies))
            last = np.random.choice(follow_words, 1, p=probabilities)[0]
            sentence += ' ' + last
            seed = last
        return sentence

    # Helpers
    def concat_strings(self, s1, s2):
        return s1 + ' ' + s2

    def search(self, range_value, ranges):

        upper_bound = len(ranges)
        # range_value = round(range_value*upper_bound)
        lower_bound = 0

        while lower_bound <= upper_bound:
            mid_index = round(lower_bound + ((upper_bound - lower_bound) / 2))  # round((lower_bound + upper_bound) / 2)
            mid = ranges[mid_index]
            # print('mid', mid_index)
            if mid['l_range'] <= range_value <= mid['u_range']:
                return mid

            elif range_value < mid['l_range']:
                upper_bound = mid_index - 1
            elif range_value > mid['u_range']:
                # if lower_bound == mid_index:
                #    break
                lower_bound = mid_index + 1

        return None


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

    # Compute training file probabilities
    unigram_training_prob = ng.get_unigram_prob(training_file)
    bigram_training_prob = ng.get_bigram_prob(training_file)
    bigram_smooth_training_prob = ng.get_bigram_smooth_prob(training_file)

    if argv[1] == '-test':
        test_file = argv[2]

        # Compute probabilities for each sentence in the test file
        with open(test_file, 'r') as file:
            for line in file:
                unigram_p = ng.get_probability(ng.get_sentence_unigram(line), unigram_training_prob)
                bigram_p = ng.get_probability(ng.get_sentence_bigram(line), bigram_training_prob)
                bigram_ps = ng.get_smooth_sentence_probability(ng.get_sentence_bigram(line),
                                                               bigram_smooth_training_prob)

                ng.print_probs(line, unigram_p, bigram_p, bigram_ps)

    elif argv[1] == '-gen':
        seed_file = argv[2]
        seeds = ng.read_seed_file(seed_file)

        for seed in seeds:
            sentences = []
            for i in range(10):
                sentences.append(ng.generate_sentence(seed))
            ng.print_gen_sentences(seed, sentences)


if __name__ == "__main__":
    main(sys.argv[1:])
