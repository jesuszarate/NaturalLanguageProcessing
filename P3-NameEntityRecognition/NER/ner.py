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
        self.featureVectors = None

        self.options = {'WORD': self.word,
                        'WORDCON': self.wordcon,
                        'POS': self.pos,
                        'POSCON': self.poscon,
                        'ABBR': self.abbr,
                        'CAP': self.cap,
                        'LOCATION': self.location
                        }
        self.optionsVec = {'WORD': self.wordVec,
                           'WORDCON': self.wordconVec,
                           'POS': self.posVec,
                           'POSCON': self.posconVec,
                           'ABBR': self.abbrVec,
                           'CAP': self.capVec,
                           'LOCATION': self.locationVec
                           }
        self.BIO_LABELS = {
            'O': 0,
            'B-PER': 1,
            'I-PER': 2,
            'B-LOC': 3,
            'I-LOC': 4,
            'B-ORG': 5,
            'I-ORG': 6
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

            parsedSentence = self.parseSentences(sentence, isTrainFile)
            if len(parsedSentence) > 0:
                sentences.append(parsedSentence)
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
        return wordcon

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
        containLoc = sentence[wordPos]['word'] in self.locations
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
        return poscon

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

    def generateReadableFeatures(self, sentences, ftypes):
        features = []
        for sentence in sentences:
            features.append(self.generateSentenceFeatures(sentence, ftypes))
        return features

    # Feature Vector

    def getFeatures(self, ftypes):
        if self.featureVectors == None:
            self.generateFeatures(ftypes)
        return self.featureVectors

    def generateFeatures(self, ftypes):
        id = 1
        self.featureVectors = dict()

        # self.setOfWords.add(self.PI)
        # self.setOfWords.add(self.OMEGA)
        self.setOfWords.add(self.UNK)
        for word in self.setOfWords:
            for ftype in ftypes:
                if ftype == 'WORD' or ftype == 'WORDCON':
                    id = self.WORDFormat(word, id, self.featureVectors, ftype, 'word')

        self.setOfPOS.add(self.PIPOS)
        self.setOfPOS.add(self.OMEGAPOS)
        self.setOfPOS.add(self.UNKPOS)
        for pos in self.setOfPOS:
            for ftype in ftypes:

                if ftype == 'POS' or ftype == 'POSCON':
                    id = self.WORDFormat(pos, id, self.featureVectors, ftype, 'pos')

        if 'CAP' in ftypes:
            self.featureVectors['capitalized'] = id
            id += 1
        if 'LOCATION' in ftypes:
            self.featureVectors['location'] = id
            id += 1
        if 'ABBR' in ftypes:
            self.featureVectors['abbreviations'] = id
            id += 1

    def getFeatureVectors(self, sentences, ftypes):
        features = []
        for sentence in sentences:
            features.append(self.generateVectorFeature(sentence, ftypes))
        return features

    def generateVectorFeature(self, sentence, ftypes):
        features = []
        # Loop through every word first
        for wordPos in range(0, len(sentence)):
            indFeatures = []
            for type in ftypes:
                res = self.optionsVec[type](wordPos, sentence)
                if isinstance(res, list):
                    indFeatures.extend(res)
                else:
                    indFeatures.append(res)

            labelCode = self.BIO_LABELS[sentence[wordPos]['label']]
            #feature = {sentence[wordPos]['word']: (sentence[wordPos]['label'], indFeatures)}
            feature = {sentence[wordPos]['word']: (labelCode, indFeatures)}
            features.append(feature)
        return features

    def wordVec(self, wordPos, sentence):
        word = 'word-{0}'.format(sentence[wordPos]['word'])

        if word in self.featureVectors:
            return '{0}:{1}'.format(self.featureVectors[word], 1)

    def wordconVec(self, wordPos, sentence):
        prevword = 'prev-word-{0}'.format(self.getWord(wordPos-1, sentence, 'word'))
        nextword = 'next-word-{0}'.format(self.getWord(wordPos+1, sentence, 'word'))

        conList = list()
        if prevword in self.featureVectors:
            conList.append('{0}:{1}'.format(self.featureVectors[prevword], 1))
        if nextword in self.featureVectors:
            conList.append('{0}:{1}'.format(self.featureVectors[nextword], 1))
        return conList

    def abbrVec(self, wordPos, sentence):
        #TODO: IMPLEMENT
        pass

    def capVec(self, wordPos, sentence):
        word = 'capitalized' if sentence[wordPos]['word'][0].isupper() else ''

        if word in self.featureVectors:
            return '{0}:{1}'.format(self.featureVectors[word], 1)

    def locationVec(self, wordPos, sentence):
        #TODO: IMPLEMENT
        pass

    def posVec(self, wordPos, sentence):
        word = 'pos-{0}'.format(sentence[wordPos]['pos'])

        if word in self.featureVectors:
            return '{0}:{1}'.format(self.featureVectors[word], 1)

    def posconVec(self, wordPos, sentence):
        #TODO: IMPLEMENT
        prevword = 'prev-pos-{0}'.format(self.getWord(wordPos-1, sentence, 'pos'))
        nextword = 'next-pos-{0}'.format(self.getWord(wordPos+1, sentence, 'pos'))

        conList = list()
        if prevword in self.featureVectors:
            conList.append('{0}:{1}'.format(self.featureVectors[prevword], 1))
        if nextword in self.featureVectors:
            conList.append('{0}:{1}'.format(self.featureVectors[nextword], 1))
        return conList

    # Helpers
    def getWord(self, wordPos, sentence, type):

        if wordPos < 0:
            if type == 'word':
                return self.PI
            elif type == 'pos':
                return self.PIPOS
        if wordPos >= len(sentence):
            if type == 'word':
                return self.OMEGA
            elif type == 'pos':
                return self.OMEGAPOS
        return sentence[wordPos]['pos']

    def fillDefaults(self, feature):
        for k, val in feature.items():
            if val == '':
                feature[k] = 'n/a'

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

    def WORDFormat(self, word, id, features, type, tag):

        if type == 'WORDCON' or type == 'POSCON':
            if word != self.OMEGAPOS:
                features['prev-{0}-{1}'.format(tag, word)] = id
                id += 1
            if word != self.PIPOS:
                features['next-{0}-{1}'.format(tag, word)] = id
                id += 1
        elif word != self.PIPOS and word != self.OMEGAPOS:
            features['{0}-{1}'.format(tag, word)] = id
            id += 1
        return id

    def POSFormat(self, pos, id, features):
        features['pos-{0}'.format(pos)] = id
        id += 1
        features['prev-pos-{0}'.format(pos)] = id
        id += 1
        features['next-pos-{0}'.format(pos)] = id
        id += 1

        return id


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

    # testSentences = NER.getSentences(getFileFormat(argv[1]))

    readableTrainFeatures = NER.generateReadableFeatures(NER.trainSentences, ftypes)
    # readableTestFeatures = NER.generateReadableFeatures(NER.testSentences, ftypes)

    WORDVEC = NER.getFeatures(ftypes)

    NER.getFeatureVectors(NER.trainSentences, ftypes)

    # genereate_trace_file(readableTestFeatures, argv[0], 'readable', 'ALL')

    # genereate_trace_file(TEST, argv[1], 'readable', 'WHAT')

    # for ftype in ftypes:
    #     genereate_trace_file(WORD, argv[0], 'readable', ftype)
    #     genereate_trace_file(TEST, argv[1], 'readable', ftype)


if __name__ == "__main__":
    main(sys.argv[1:])
