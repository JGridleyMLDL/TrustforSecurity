import json
import numpy
from dataclasses import dataclass
from collections import defaultdict

### Default Values ###
gamma = 0.5
initialPrecision = 0.8
initialRecall = 0.8
initialAccuracy = 0.8



### Data Classes ###
@dataclass
class Extractor:
    precision: float
    recall: float
    presenceVote: float
    absenceVote: float

    def __init__(self, precision = initialPrecision, recall = initialRecall):
        self.precision = precision
        self.recall = recall
        self.updatePresenceAndAbsenceVote()

    #Equation 7
    def getSpecificity(self) -> float:
        return (gamma/(1.0 - gamma)) * ((1.0 - self.precision)/self.precision) * self.recall

    #Equation 12
    def updatePresenceAndAbsenceVote(self) -> None:
        specificity = self.getSpecificity()
        self.presenceVote = numpy.log(self.recall) - numpy.log(specificity)
        self.absenceVote = numpy.log(1.0 - self.recall) - numpy.log(1.0 - specificity)

@dataclass
class Source:
    accuracy: float

    def __init__(self, accuracy = initialAccuracy):
        self.accuracy = accuracy



### Estimating C ###
def sigmoid(x):
    return (1.0/(1.0 + numpy.exp(-x)))

#Equation 14 (Replace with 31 for Extractors with Confidence Values)
def getVoteCount(sourceDataItemSlice, value, extractors):
    voteCount = 0
    for extractorIndex in range(sourceDataItemSlice.size):
        if sourceDataItemSlice[extractorIndex] == value:
            voteCount += extractors[extractorIndex].presenceVote
        else:
            voteCount += extractors[extractorIndex].absenceVote
    return voteCount

#Equation 15
def getProbabilityCwdvGivenXwdv(sourceDataItemSlice, value, extractors, alpha):
    return sigmoid(getVoteCount(sourceDataItemSlice, value, extractors) + numpy.log(alpha/(1.0 - alpha)))


### Multilayer Algorithm ###
#Values Cube is a 3D Matrix with Axis (Extactor, Source, Data Item) with Value as the entries
def multilayer(valuesCube, maxIterations):
    extractors = defaultdict(Extractor)
    sources = defaultdict(Source)
    pass


def getMatrixFromJSON(jsonData):

    pass


if __name__ == "__main__":
    multilayer(numpy.array([[["0", "0", "0", "0"],
                  ["0", "1", "0", "1"]],
                  [["1", "1", "1", "1"],
                  ["0", "0", "2", "2"]],
                  [["2", "2", "2", "2"],
                  ["2", "0", "1", "2"]]]), 100)
    #Read input data and call the model
    #with open("data.json", "r") as f:
    #    data = f.read()
    # Parsing the file
    #json_data = json.loads(data)
