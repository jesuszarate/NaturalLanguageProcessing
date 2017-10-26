
class featureVector:

    def __init__(self):
        self.BIO_LABELS = {
             'O': 0,
             'B-PER': 1,
             'I-PER': 2,
             'B-LOC': 3,
             'I-LOC': 4,
             'B-ORG': 5,
             'I-ORG': 6
        }

    def generateFeatureVector(self, features):
        pass
