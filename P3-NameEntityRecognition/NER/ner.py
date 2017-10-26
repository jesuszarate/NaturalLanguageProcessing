import sys
from pathlib import Path

import re


class ner:
    def __init__(self, trainFileName, testFileName, locationsFileName):

        self.UNK = 'UNK'
        self.UNKPOS = 'UNKPOS'
        self.PI = 'PHI'
        self.PIPOS = 'PHIPOS'
        self.OMEGA = 'OMEGA'
        self.OMEGAPOS = 'OMEGAPOS'
        self.setOfWords = set()
        self.setOfPOS = set()
        self.trainSentences = self.getSentences(trainFileName, True)
        self.testSentences = self.getSentences(testFileName, False)
        self.locationFileName = locationsFileName
        self.locations = None

        self.options = {'WORD': self.word,
                        'WORDCON': self.wordcon,
                        'POS': self.pos,
                        'POSCON': self.poscon,
                        'ABBR': self.abbr,
                        'CAP': self.cap,
                        'LOCATION': self.location
                        }

    def getLocations(self, locationsFileName):
        self.locations = set()
        with open(locationsFileName, 'r') as f:
            for line in f:
                self.locations.add(line.strip())

    def getSentences(self, filename, isTrainFile=False):
        sentences = []
        with open(filename, 'r') as f:
            sentence = ''
            for line in f:
                if line == '\n':
                    parsedSentence = self.parseSentences(sentence, isTrainFile)
                    if len(parsedSentence) > 0:
                        sentences.append(parsedSentence)
                    sentence = ''
                    continue
                sentence += line
        return sentences

    def parseSentences(self, sentence, isTrainFile):
        listOfWords = []
        words = sentence.split('\n')
        for word in words:
            words = word.split()
            if len(words) > 0:
                if isTrainFile:
                    self.setOfWords.add(words[2])
                    self.setOfPOS.add(words[1])
                listOfWords.append({'label': words[0], 'pos': words[1], 'word': words[2]})

        return listOfWords

    def word(self, wordPos, sentence):
        word = sentence[wordPos]
        return word['word'] if word['word'] in self.setOfWords else self.UNK

    def wordcon(self, wordPos, sentence):
        wordcon = self.PI

        if wordPos > 0:
            wordcon = sentence[wordPos - 1]['word']
        if wordPos + 1 < len(sentence):
            wordcon += ' ' + sentence[wordPos + 1]['word']
        else:
            wordcon += ' ' + self.OMEGA
        return  wordcon

    def abbr(self, wordPos, sentence):
        word = sentence[wordPos]

        alphaNumPeriod = re.compile('^[a-zA-Z0-9_(\.)+]*$')

        if str.endswith(word['word'], '.') and \
                alphaNumPeriod.match(word['word']) and \
                        len(word['word']) <= 4:
            return 'yes'
        else:
            return 'no'

    def cap(self, wordPos, sentence):
        return 'yes' if sentence[wordPos]['word'][0].isupper() else 'no'

    def location(self, wordPos, sentence):
        if self.locations == None or len(self.locations) <= 0:
            self.getLocations(self.locationFileName)
        containLoc =  sentence[wordPos]['word'] in self.locations
        return 'yes' if containLoc else 'no'

    def pos(self, wordPos, sentence):
        word = sentence[wordPos]
        return word['pos'] if word['pos'] in self.setOfPOS else self.UNKPOS

    def poscon(self, wordPos, sentence):
        poscon = self.PIPOS

        if wordPos > 0:
            poscon = sentence[wordPos - 1]['pos']
        if wordPos + 1 < len(sentence):
            poscon += ' ' + sentence[wordPos + 1]['pos']
        else:
            poscon += ' ' + self.OMEGAPOS
        return  poscon

    def generateSentenceFeatures(self, sentence, ftypes):
        features = []
        # Loop through every word first
        for wordPos in range(0, len(sentence)):
            feature = self.featureTemplate()
            for type in ftypes:
                feature[type] = self.options[type](wordPos, sentence)

            self.fillDefaults(feature)
            features.append(feature)
        return features

    def generateFeatures(self, sentences, ftypes):
        features = []
        for sentence in sentences:
            features.append(self.generateSentenceFeatures(sentence, ftypes))
        return features

    #Feature Vector
    def generateFeatureVectors(self):

        id = 1
        features = dict()
        for word in self.setOfWords:
            features['word-{0}'.format(word)] = id
            id += 1

        for pos in self.setOfPOS:
            features['pos-{0}'.format(pos)] = id
            id += 1
            features['prev-pos-{0}'.format(pos)] = id
            id += 1
            features['next-pos-{0}'.format(pos)] = id
            id += 1

    def fillDefaults(self, feature):
        for k, val in feature.items():
            if val == '':
                feature[k] = 'n/a'

    # Helpers
    def featureTemplate(self):
        featureTemplate = {
            'WORD': '',
            'WORDCON': '',
            'POS': '',
            'POSCON': '',
            'ABBR': '',
            'CAP': '',
            'LOCATION': ''}
        return featureTemplate




def does_file_exist(filename):
    file = Path('ner-input-files/{0}'.format(filename))
    if file.is_file():
        return True
    return False


def getFileFormat(filename):
    return 'ner-input-files/{0}'.format(filename)


# Writing files
def genereate_trace_file(data, name, type, extension=''):
    extension = extension if extension == '' else '.' + extension
    with open('OutputFiles/{0}.{1}{2}'.format(name, type, extension), 'w') as of:
        for sentence in data:
            for line in sentence:
                for k, v in line.items():
                    of.write('{0}: {1}\n'.format(k, v))
                of.write('\n')


def main(argv):
    if len(argv) < 4:
        print('python ner <train file> <test file> <locations file> WORD [... <ftype >]')
        sys.exit(2)

    if not (does_file_exist(argv[0])):
        print('In argument 1 file does not exist: {0}'.format(argv[0]))
        sys.exit(2)
    elif not does_file_exist(argv[1]):
        print('In argument 2 file does not exist: {0}'.format(argv[1]))
        sys.exit(2)
    elif not does_file_exist(argv[2]):
        print('In argument 2 file does not exist: {0}'.format(argv[2]))
        sys.exit(2)

    ftypes = []
    ftypePos = 3

    for pos in range(ftypePos, len(argv)):
        ftypes.append(argv[pos])

    NER = ner(getFileFormat(argv[0]), getFileFormat(argv[1]), getFileFormat(argv[2]))

    #testSentences = NER.getSentences(getFileFormat(argv[1]))

    WORD = NER.generateFeatures(NER.trainSentences, ftypes)
    TEST = NER.generateFeatures(NER.testSentences, ftypes)

    WORDVEC = NER.generateFeatureVectors(NER.trainSentences, ftypes)

    genereate_trace_file(WORD, argv[0], 'readable', 'ALL')
    #genereate_trace_file(TEST, argv[1], 'readable', 'WHAT')

    # for ftype in ftypes:
    #     genereate_trace_file(WORD, argv[0], 'readable', ftype)
    #     genereate_trace_file(TEST, argv[1], 'readable', ftype)

if __name__ == "__main__":
    main(sys.argv[1:])
