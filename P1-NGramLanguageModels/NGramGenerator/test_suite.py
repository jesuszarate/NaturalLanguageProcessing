import unittest
import NGramGenerator.ngrams as ngrams
from math import log


class Test(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.filename = 'myTest.txt'
        self.train_filename = '../train.txt'

        self.bigram_probs = {
            'phi hello': 1 / 14,
            'hello world': 2 / 14,
            'world how': 1 / 14,
            'phi how': 1 / 14,
            'how are': 2 / 14,
            'are you': 2 / 14,
            'you how': 1 / 14,
            'you doing': 1 / 14,
            'doing hello': 1 / 14,
            'world well': 1 / 14,
            'phi well': 1 / 14,
            'well fine': 1 / 14,
            'fine you': 1 / 14}

        self.unigrams_freqs = dict(hello=2, world=2, how=2, are=2, you=3, doing=1, well=1, fine=1)

        self.unigram_probs = dict(hello=2 / 14, world=2 / 14, how=2 / 14, are=2 / 14, you=3 / 14, doing=1 / 14,
                                  well=1 / 14,
                                  fine=1 / 14)

    def test_unigram_freq(self):
        """
        Test unigram_freq(filename)
        """

        frequencies = ngrams.unigram_freq(self.filename)
        for key, val in self.unigrams_freqs.items():
            self.assertEqual(frequencies[key], val)

    def test_compute_prob(self):
        """
        Testing compute_prob(frequencies):
        """
        filename = 'myTest.txt'

        frequencies = ngrams.unigram_freq(filename)
        probs = ngrams.compute_prob(frequencies)

        for key, val in self.unigram_probs.items():
            self.assertEqual(probs[key], val)

    def test_compute_prob_bigrams(self):
        """
        Testing computing the probabilities for bigrams
        """
        # filename = 'train.txt'

        # hello world how are you
        # How are you doing hello world
        # well fine you

        bigram_training_prob = ngrams.get_bigram_prob(self.filename)

        for key, val in self.bigram_probs.items():
            self.assertEqual(self.bigram_probs[key], val)

    def test_create_bigram_freq(self):
        for i in ngrams.bigram_freq(self.filename):
            print(i)

    def test_log_probability(self):
        bigram_training_prob = ngrams.get_bigram_prob(self.filename)
        bigramp_p = ngrams.get_log_probability(ngrams.get_sentence_bigram('hello'), bigram_training_prob)

        # for i in ngrams.bigram_freq('../train.txt').keys():
        #    print(i)

        # self.assertEqual(bigramp_p, log(1 / 14, 2))

    #def test_file_size(self):

    def test_write_probs_to_file(self):
        bigram_training_prob = ngrams.get_bigram_prob(self.train_filename)

        with open('somefile.txt', 'w') as file:
            for k, val in bigram_training_prob.items():
                file.write(k + " : " + str(val) + '\n')
