import sys
from pathlib import Path

class eval:
    def __init__(self, predictionFileName, goldFileName):
        self.B = 'B'
        self.I = 'I'
        self.O = 'O'

        self.predictions = self.readFile(predictionFileName)
        self.gold = self.readFile(goldFileName)

    def readFile(self, fileName):
        with open(fileName, 'r') as f:

            pos = 0
            currentB = None
            entityList = list()
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
                        entityList.append(currentEntity)

                    # Record new entity being computed
                    currentEntity = ({entry['entity']: [entry['word']]}, {'from': pos, 'to':pos})
                    currentB = entry


                elif currentB != None:
                    # Takes care of I and O
                    if entry['label'] == self.O or entry['entity'] != currentB['entity']:
                        entityList.append(currentEntity)
                        currentEntity = None
                        currentB = None


                # Case where I belongs to the current B
                if currentB != None and entry['label'] == self.I and entry['entity'] == currentB['entity']:
                    currentEntity[0][entry['entity']].append(entry['word'])
                    currentEntity[1]['to'] = pos
                pos += 1
        return entityList

    def evaluate(self):
        pass
        #for pos in range(0, )


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

    ev.evaluate()

if __name__ == "__main__":
    main(sys.argv[1:])
