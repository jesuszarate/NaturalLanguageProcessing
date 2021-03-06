import sys
import logging
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
        return self.containsWord(word['word'])
        # return word['word'] if word['word'] in self.setOfWords else self.UNK

    def wordcon(self, wordPos, sentence):
        wordcon = self.PI

        if wordPos > 0:
            wordcon = self.containsWord(sentence[wordPos - 1]['word'])
        if wordPos + 1 < len(sentence):
            wordcon += ' ' + self.containsWord(sentence[wordPos + 1]['word'])
        else:
            wordcon += ' ' + self.OMEGA

        return wordcon

    def abbr(self, wordPos, sentence):
        word = sentence[wordPos]

        alphaNumPeriod = re.compile('^[a-zA-Z\.]*\.$')

        if alphaNumPeriod.match(word['word']) and \
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

    def generateFeatures(self, ftypes):
        id = 1
        self.featureVectors = dict()

        self.setOfWords.add(self.PI)
        self.setOfWords.add(self.OMEGA)
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
            self.featureVectors['abbreviation'] = id
            id += 1

    def getFeatureVectors(self, sentences, ftypes):
        self.getFeatures(ftypes)

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
                elif res != None:
                    indFeatures.append(res)

            labelCode = self.BIO_LABELS[sentence[wordPos]['label']]
            feature = {sentence[wordPos]['word']: (labelCode, indFeatures)}
            features.append(feature)
        return features

    def wordVec(self, wordPos, sentence):
        word = 'word-{0}'.format(sentence[wordPos]['word'])

        if word in self.featureVectors:
            return self.getFeatTuple(word)

    def wordconVec(self, wordPos, sentence):
        prevword = 'prev-word-{0}'.format(self.getWord(wordPos - 1, sentence, 'word'))
        nextword = 'next-word-{0}'.format(self.getWord(wordPos + 1, sentence, 'word'))

        conList = list()
        if prevword in self.featureVectors:
            conList.append(self.getFeatTuple(prevword))
        if nextword in self.featureVectors:
            conList.append(self.getFeatTuple(nextword))
        return conList

    def abbrVec(self, wordPos, sentence):

        word = 'abbreviation' if 'yes' == self.abbr(wordPos, sentence) else ''

        if word in self.featureVectors:
            return self.getFeatTuple(word)
        return None

    def capVec(self, wordPos, sentence):
        word = 'capitalized' if sentence[wordPos]['word'][0].isupper() else ''

        if word in self.featureVectors:
            # return '{0}:{1}'.format(self.featureVectors[word], 1)
            return self.getFeatTuple(word)
        return None

    def locationVec(self, wordPos, sentence):
        word = 'location' if 'yes' == self.location(wordPos, sentence) else ''

        if word in self.featureVectors:
            # return '{0}:{1}'.format(self.featureVectors[word], 1)
            return self.getFeatTuple(word)

    def posVec(self, wordPos, sentence):
        word = 'pos-{0}'.format(sentence[wordPos]['pos'])

        if word in self.featureVectors:
            # return '{0}:{1}'.format(self.featureVectors[word], 1)
            return self.getFeatTuple(word)

    def posconVec(self, wordPos, sentence):
        prevword = 'prev-pos-{0}'.format(self.getWord(wordPos - 1, sentence, 'pos'))
        nextword = 'next-pos-{0}'.format(self.getWord(wordPos + 1, sentence, 'pos'))

        conList = list()
        if prevword in self.featureVectors:
            # conList.append('{0}:{1}'.format(self.featureVectors[prevword], 1))
            conList.append(self.getFeatTuple(prevword))
        if nextword in self.featureVectors:
            conList.append(self.getFeatTuple(nextword))
            # conList.append('{0}:{1}'.format(self.featureVectors[nextword], 1))
        return conList

    # Helpers
    def containsWord(self, word):
        return word if word in self.setOfWords else self.UNK

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
        return sentence[wordPos][type]

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
            if word != self.OMEGAPOS and word != self.OMEGA:
                features['prev-{0}-{1}'.format(tag, word)] = id
                id += 1
            if word != self.PIPOS and word != self.PI:
                features['next-{0}-{1}'.format(tag, word)] = id
                id += 1
        elif word != self.PIPOS and word != self.OMEGAPOS and \
                        word != self.PI and word != self.OMEGA:
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

    def getFeatTuple(self, word):
        return (self.featureVectors[word], 1)

    def flattenFeatureVectors(self, featVecs):
        flattenedList = list()
        for word in featVecs:
            for feat in word:
                for name, vec in feat.items():
                    tempList = [vec[0]]
                    tempList.extend(sorted(vec[1], key=self.featComperator))
                    flattenedList.append(tempList)
        return flattenedList

    def featComperator(self, feat):
        return feat[0]


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
    fileLocation = getOutputFileLocation(name, type, extension)
    print('Writing to: {0}'.format(fileLocation))
    with open(fileLocation, 'w') as of:
        for sentence in data:
            for line in sentence:
                for k, v in line.items():
                    of.write('{0}: {1}\n'.format(k, v))
                of.write('\n')


def writeFeatureVectorsToFile(flattenFeatVec, name, type, extension=''):
    extension = extension if extension == '' else '.' + extension
    fileLocation = getOutputFileLocation(name, type, extension)
    print('Writing to: {0}'.format(fileLocation))
    with open(fileLocation, 'w') as of:
        # with open('OutputFiles/{0}.{1}{2}'.format(name, type, extension), 'w') as of:

        for line in flattenFeatVec:
            of.write('{0} '.format(line[0]))

            for i in range(1, len(line) - 1):
                entry = line[i]
                of.write('{0}:{1} '.format(entry[0], entry[1]))
            if len(line) > 1:
                entry = line[len(line) - 1]
                of.write('{0}:{1} '.format(entry[0], entry[1]))
            of.write('\n')


def getOutputFileLocation(name, type, extension):
    return 'OutputFiles/{0}.{1}{2}'.format(name, type, extension)


def getReadableFeatures(NER, data, fileName, ftypes, type):
    readableTrainFeatures = NER.generateReadableFeatures(data, ftypes)
    genereate_trace_file(readableTrainFeatures, fileName, 'readable', type)


def getFeatureVectors(NER, fileName, ftypes, type, test=False):
    sentences = NER.testSentences if test else NER.trainSentences
    featVec = NER.getFeatureVectors(sentences, ftypes)
    flattenFeatVec = NER.flattenFeatureVectors(featVec)
    writeFeatureVectorsToFile(flattenFeatVec, fileName, 'vector', type)


def main(argv):
    if len(argv) < 4:
        print('python ner <train file> <test file> <locations file> WORD [... <ftype >]')
        sys.exit(2)

    if not (does_file_exist(argv[0])):
        print('In argument 1 file does not exist: {0}'.format(argv[0]))
        print('Note: Make sure the input files are stored in the ner-input-files folder')
        sys.exit(2)
    elif not does_file_exist(argv[1]):
        print('In argument 2 file does not exist: {0}'.format(argv[1]))
        print('Note: Make sure the input files are stored in the ner-input-files folder')
        sys.exit(2)
    elif not does_file_exist(argv[2]):
        print('In argument 2 file does not exist: {0}'.format(argv[2]))
        print('Note: Make sure the input files are stored in the ner-input-files folder')
        sys.exit(2)

    ftypes = []
    ftypePos = 3

    for pos in range(ftypePos, len(argv)):
        ftypes.append(argv[pos])

    NER = ner(getFileFormat(argv[0]), getFileFormat(argv[1]), getFileFormat(argv[2]))

    # testSentences = NER.getSentences(getFileFormat(argv[1]))

    # To produce the readable features one param at a time
    if len(ftypes) < 3:
        type = ftypes[len(ftypes) - 1]
        getReadableFeatures(NER, NER.trainSentences, argv[0], ftypes, type) # For train
        getReadableFeatures(NER, NER.testSentences, argv[1], ftypes, type) # For test

        getFeatureVectors(NER, argv[0], ftypes, type) # For train
        getFeatureVectors(NER, argv[1], ftypes, type, test=True) # For test

    elif len(ftypes) == 7:
        getReadableFeatures(NER, NER.trainSentences, argv[0], ftypes, 'ALL')
        getReadableFeatures(NER, NER.testSentences, argv[1], ftypes, 'ALL')

        getFeatureVectors(NER, argv[0], ftypes, 'ALL') # For train
        getFeatureVectors(NER, argv[1], ftypes, 'ALL', test=True) # For test


if __name__ == "__main__":
    main(sys.argv[1:])
