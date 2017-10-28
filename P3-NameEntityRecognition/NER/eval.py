import sys
from pathlib import Path

class eval:
    def __init__(self, predictionFileName, goldFileName):
        self.B = 'B'
        self.I = 'I'
        self.O = 'O'
        self.labels = ['PER', 'LOC', 'ORG']
        predLen, self.predictions = self.readFile(predictionFileName)
        goldLen, self.gold = self.readFile(goldFileName)
        self.templateList = self.getTemplateList()

        self.maxLen = goldLen

    def createTemplate(self):
        return {
            'Correct': None,
            'Recall' : 0,
            'TotRecall' : 0,
            'Precision' : 0,
            'TotPrecision' : 0
        }

    def getTemplateList(self):
        tList = list()
        for label in self.labels:
            tList.append(self.createTemplate())
        return tList

    def getLabel(self, pos):
        if pos == 0:
            return 'PER'
        if pos == 1:
            return 'LOC'
        if pos == 2:
            return 'ORG'

    def getTemplate(self, label):
        if label == 'PER':
            return self.templateList[0]
        if label == 'LOC':
            return self.templateList[1]
        if label == 'ORG':
            return self.templateList[2]

    def readFile(self, fileName):
        with open(fileName, 'r') as f:

            pos = 0
            currentB = None
            currentPosB = 0
            entityList = dict()
            currentEntity = None
            for line in f:
                word = line.split()
                BIO = word[0].split('-')

                if len(BIO) > 1:
                    entry = {'word': word[1], 'label':BIO[0], 'entity':BIO[1]}
                else:
                    entry = {'word': word[1], 'label':BIO[0], 'entity':None}

                if entry['label'] == self.B:
                    # Save the old entity
                    if currentEntity != None:
                        entityList[currentPosB] = currentEntity

                    # Record new entity being computed
                    currentEntity = ({'entity' : entry['entity'], 'labels':[entry['word']]}, {'from': pos, 'to':pos})
                    currentB = entry
                    currentPosB = pos


                elif currentB != None:
                    # Takes care of I and O
                    if entry['label'] == self.O or entry['entity'] != currentB['entity']:
                        entityList[currentPosB] = currentEntity
                        currentEntity = None
                        currentB = None


                # Case where I belongs to the current B
                if currentB != None and entry['label'] == self.I and entry['entity'] == currentB['entity']:
                    currentEntity[0]['labels'].append(entry['word'])
                    currentEntity[1]['to'] = pos
                pos += 1
        return pos, entityList


    def evaluate(self):
        """
        Evaluates the prediction and the gold, and stores the results in self.templateList
        """
        for pos in range(0, self.maxLen):

            if pos in self.gold and pos in self.predictions:
                entryTypeGold = self.gold[pos]
                entryTypePred = self.predictions[pos]

                entityGold = entryTypeGold[0]['entity']
                entityPred = entryTypePred[0]['entity']

                fromGold, toGold = entryTypeGold[1]['from'], entryTypeGold[1]['to'],
                fromPred, toPred = entryTypePred[1]['from'], entryTypePred[1]['to'],

                if entityGold == entityPred and (fromGold == fromPred and toGold == toPred):
                    self.updateTemplate(entityGold, entryTypeGold[0]['labels'], fromGold, toGold)

            if pos in self.gold:
                entity = self.gold[pos][0]['entity']
                self.updateTotRecal(entity)

            if pos in self.predictions:
                entity = self.predictions[pos][0]['entity']
                self.updateTotPrecision(entity)


    def writeEvaluation(self, outputFile):
        self.evaluate() # Evaluate the template list

        numRecall = 0
        denumRecall = 0

        numPrec = 0
        denumPrec = 0

        with open(outputFile, 'w') as of:
            pos = 0
            for template in self.templateList:
                correct = 'NONE'
                if template['Correct'] != None:
                    correct = self.formatList(template['Correct'])
                label = self.getLabel(pos)
                print('Correct {0} = {1}'.format(label, correct))

                numRecall += template['Recall']
                denumRecall += template['TotRecall']
                frac = '{0}/{1}'.format(template['Recall'], template['TotRecall'])
                print('Recall {0} = {1}'.format(label, 'n/a' if frac == '0/0' else frac))#template['Recall'], template['TotRecall']))

                numPrec += template['Precision']
                denumPrec += template['TotPrecision']
                frac = '{0}/{1}'.format(template['Precision'], template['TotPrecision'])
                print('Precision {0} = {1}'.format(label, 'n/a' if frac == '0/0' else frac))
                print()

            frac = '{0}/{1}'.format(numRecall, denumRecall)
            print('Average Recall = {0}'.format('n/a' if frac == '0/0' else frac))

            frac = '{0}/{1}'.format(numPrec, denumPrec)
            print('Average Precision = {0}'.format('n/a' if frac == '0/0' else frac))



    def formatList(self, vList):
        result = ''
        if len(vList) < 1:
            return result

        for value in vList:
            result += '{0} | '.format(value)
        return result[:-2]

    def updateTotRecal(self, entity):
        template = self.getTemplate(entity)

        template['TotRecall'] += 1

    def updateTotPrecision(self, entity):
        template = self.getTemplate(entity)

        template['TotPrecision'] += 1

    def updateTemplate(self, entity, labels, From, To):
        template = self.getTemplate(entity)

        if template['Correct'] == None:
            template['Correct'] = list()


        template['Correct'].extend([self.toString(labels) + '[{0}-{1}]'.format(From+1, To+1)])
        template['Recall'] += 1
        template['Precision'] += 1

    #Helpers
    def toString(self, vList):
        result = ''
        if len(vList) < 1:
            return  result
        for string in vList:
            result += '{0} '.format(string)
        return result[:-1]

def getFileFormat(filename):
    return 'eval-program-files/{0}'.format(filename)

def does_file_exist(filename):
    file = Path(getFileFormat(filename))
    if file.is_file():
        return True
    return False

def main(argv):
    if len(argv) != 2:
        print('python eval <prediction file> <gold file>')
        print('Note: Make sure the input files are stored in the eval-program-files folder')
        sys.exit(2)

    if not (does_file_exist(argv[0])):
        print('In argument 1 file does not exist: {0}'.format(argv[0]))
        print('Note: Make sure the input files are stored in the eval-program-files folder')
        sys.exit(2)
    elif not does_file_exist(argv[1]):
        print('In argument 2 file does not exist: {0}'.format(argv[1]))
        print('Note: Make sure the input files are stored in the eval-program-files folder')

        sys.exit(2)

    ev = eval(getFileFormat(argv[0]), getFileFormat(argv[1]))

    ev.writeEvaluation('eval.txt')

if __name__ == "__main__":
    main(sys.argv[1:])
