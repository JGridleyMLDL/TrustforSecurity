import sys
import json
import numpy
from dataclasses import dataclass
from collections import defaultdict

### Default Values ###
gamma = 0.44
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

    def __init__(self, precision=initialPrecision, recall=initialRecall):
        self.precision = precision
        self.recall = recall
        self.updatePresenceAndAbsenceVote()

    # Equation 7
    def getSpecificity(self) -> float:
        return (gamma / (1.0 - gamma)) * ((1.0 - self.precision) / self.precision) * self.recall

    # Equation 12
    def updatePresenceAndAbsenceVote(self) -> None:
        specificity = self.getSpecificity()
        self.presenceVote = numpy.log(self.recall) - numpy.log(specificity)
        self.absenceVote = numpy.log(1.0 - self.recall) - numpy.log(1.0 - specificity)


@dataclass
class Source:
    accuracy: float

    def __init__(self, accuracy=initialAccuracy):
        self.accuracy = accuracy


### Estimating C ###
def sigmoid(x):
    return (1.0 / (1.0 + numpy.exp(-x)))


# Equation 14 (Change to 31 later)
def getVoteCount(sourceDataItemSlice, value, extractors):
    voteCount = 0.0
    for extractorIndex in range(sourceDataItemSlice.size):
        if sourceDataItemSlice[extractorIndex] == value:
            voteCount += extractors[extractorIndex].presenceVote
        else:
            voteCount += extractors[extractorIndex].absenceVote
    return voteCount


# Equation 15
def getProbabilityCwdvGivenXwdv(sourceDataItemSlice, value, extractors, alpha):
    return sigmoid(getVoteCount(sourceDataItemSlice, value, extractors) + numpy.log(alpha / (1.0 - alpha)))


### Estimating V ###
# Equation 23, 24, and 25
def getProbabilityVdEqualsVGivenX(dataItemDomainSlice, relevantValue, sources, probabilityCwdvGivenXwdvSlice):
    numerator = 0.0
    denominator = 0.0
    n = len(dataItemDomainSlice) - 1.0
    if n == 0:  # If there is only one value extracted for a given data item, then it MUST be the correct value for that data item (not necessarily true)
        return 1.0
    for value in dataItemDomainSlice:
        for sourceIndex in range(len(sources)):
            if value in probabilityCwdvGivenXwdvSlice[
                sourceIndex]:  # Assume that if a triple was never extracted for a particular source then the probability is zero
                expVCV = numpy.exp(probabilityCwdvGivenXwdvSlice[sourceIndex][value] * numpy.log(
                    (n * sources[sourceIndex].accuracy) / (1.0 - sources[sourceIndex].accuracy)))
                if value == relevantValue:
                    numerator += expVCV
                denominator += expVCV
    return numerator / denominator


### Estimating Accuracy ###
# Equation 28
def getAccuracyForSource(sourceSliceOfCwdv, probabilityVdEqualsVGivenX):
    numerator = 0.0
    denominator = 0.0
    for dataItemIndex in range(len(sourceSliceOfCwdv)):
        if sourceSliceOfCwdv[dataItemIndex]:
            numerator += sourceSliceOfCwdv[dataItemIndex][1] * probabilityVdEqualsVGivenX[dataItemIndex][
                sourceSliceOfCwdv[dataItemIndex][0]]
            denominator += sourceSliceOfCwdv[dataItemIndex][1]
    return numerator / denominator


### Estimating Precision and Recall ###
# Equation 29 and 30 (Change to 32 and 33 later)
def getPrecisionAndRecallForExtractor(extractorSliceOfValueCube, probabilityCwdvGivenXwdv, denominatorRecall):
    numerator = 0.0
    denominatorPrecision = 0.0
    for sourceIndex in range(extractorSliceOfValueCube.shape[0]):
        for dataItemIndex in range(extractorSliceOfValueCube.shape[1]):
            if (extractorSliceOfValueCube[sourceIndex][dataItemIndex]):
                if extractorSliceOfValueCube[sourceIndex][dataItemIndex] in probabilityCwdvGivenXwdv[sourceIndex][
                    dataItemIndex]:  # This seems wrong, double check
                    numerator += probabilityCwdvGivenXwdv[sourceIndex][dataItemIndex][
                        extractorSliceOfValueCube[sourceIndex][dataItemIndex]]
                denominatorPrecision += 1.0
    return numerator / denominatorPrecision, numerator / denominatorRecall


### Calculating Alpha ###
def getAlpha(probabilityVdEqualsVGivenX, accuracy):
    return probabilityVdEqualsVGivenX * accuracy + (1 - probabilityVdEqualsVGivenX) * (1 - accuracy)


### Multilayer Algorithm ###
# Values Cube is a 3D Matrix with Axis (Extactor, Source, Data Item) with Value as the entries
# sourceDataItemDomain stores a set of all extracted values by source and data item in 2D matrix
# dataItemDomain stores a set of all extracted values by data item in a 2D list
def multilayer(valuesCube, sourceDataItemDomain, dataItemDomain, maxIterations):
    # Initialize all necessary data structures
    extractors = numpy.array([Extractor() for _ in range(valuesCube.shape[0])],
                             dtype="object")  # Stores all extractors in list by extractor index
    sources = numpy.array([Source() for _ in range(valuesCube.shape[1])],
                          dtype="object")  # Stores all sources in list by source index
    probabilityCwdvGivenXwdv = numpy.array(
        [[dict() for _ in range(valuesCube.shape[2])] for _ in range(valuesCube.shape[1])],
        dtype="object")  # 2D list by source and data item index holding a map from value to P(Cwdv|Xwdv)
    argmaxProbabilityCwdvGivenXwdv = numpy.array([[None] * valuesCube.shape[2] for _ in range(valuesCube.shape[1])],
                                                 dtype="object")  # 2D list by source and data item index holding (data item index, value, P(Cwdv|Xwdv)) tuple that is argmax P(Cwdv|Xwdv)
    probabilityVdEqualsVGivenX = numpy.array([dict() for _ in range(valuesCube.shape[2])],
                                             dtype="object")  # 1D List by data item index holding a map from value to P(Vd = v|Xd)
    alphas = numpy.array(
        [[defaultdict(lambda: 0.5) for _ in range(valuesCube.shape[2])] for _ in range(valuesCube.shape[1])],
        dtype="object")  # 2D list by source and data item index holding map from value to alpha

    # Begin Iterative Algorithm
    for _ in range(maxIterations):
        print("ITERATION")
        # Estimate C
        for sourceIndex in range(len(sourceDataItemDomain)):
            for dataItemIndex in range(len(sourceDataItemDomain[sourceIndex])):
                for value in sourceDataItemDomain[sourceIndex][dataItemIndex]:
                    tmp = getProbabilityCwdvGivenXwdv(valuesCube[:, sourceIndex, dataItemIndex], value, extractors,
                                                      alphas[sourceIndex][dataItemIndex][value])
                    probabilityCwdvGivenXwdv[sourceIndex][dataItemIndex][value] = tmp
                    if not argmaxProbabilityCwdvGivenXwdv[sourceIndex][dataItemIndex] or \
                            argmaxProbabilityCwdvGivenXwdv[sourceIndex][dataItemIndex][1] < tmp:
                        argmaxProbabilityCwdvGivenXwdv[sourceIndex][dataItemIndex] = (value, tmp)

        # Estimate V
        for dataItemIndex in range(len(dataItemDomain)):
            for value in dataItemDomain[dataItemIndex]:
                probabilityVdEqualsVGivenX[dataItemIndex][value] = getProbabilityVdEqualsVGivenX(
                    dataItemDomain[dataItemIndex], value, sources, probabilityCwdvGivenXwdv[:, dataItemIndex])

        # Estimate Accuracy
        for sourceIndex in range(len(sources)):
            sources[sourceIndex].accuracy = getAccuracyForSource(argmaxProbabilityCwdvGivenXwdv[sourceIndex],
                                                                 probabilityVdEqualsVGivenX)

        # Estimate Precision and Recall
        denominatorRecall = sum(
            value for values in [values.values() for values in probabilityCwdvGivenXwdv.flatten()] for value in values)
        for extractorIndex in range(len(extractors)):
            extractors[extractorIndex].precision, extractors[extractorIndex].recall = getPrecisionAndRecallForExtractor(
                valuesCube[extractorIndex], probabilityCwdvGivenXwdv, denominatorRecall)
            extractors[extractorIndex].updatePresenceAndAbsenceVote()

        # Check for Convergence

        # Calculate Alpha
        for sourceIndex in range(len(sourceDataItemDomain)):
            for dataItemIndex in range(len(sourceDataItemDomain[sourceIndex])):
                for value in sourceDataItemDomain[sourceIndex][dataItemIndex]:
                    alphas[sourceIndex][dataItemIndex][value] = getAlpha(
                        probabilityVdEqualsVGivenX[dataItemIndex][value], sources[sourceIndex].accuracy)
    error_Checking(valuesCube, sources)
    return sources, extractors


def main():
    '''
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} [filename]")
        exit()
    '''
    with open("multilayerinput_small.json", 'r') as inputFile:
        data = json.load(inputFile)

    extractorToIndex = {}
    sourceToIndex = {}
    dataItemToIndex = {}

    for extractor in data:
        if extractor not in extractorToIndex:
            extractorToIndex[extractor] = len(extractorToIndex)
        for source in data[extractor]:
            if source not in sourceToIndex:
                sourceToIndex[source] = len(sourceToIndex)
            for triple in data[extractor][source]:
                dataItem = (triple[0], triple[1])
                value = triple[2]
                if dataItem not in dataItemToIndex:
                    dataItemToIndex[dataItem] = len(dataItemToIndex)

    valueCube = numpy.empty((len(extractorToIndex), len(sourceToIndex), len(dataItemToIndex)), dtype="object")
    sourceDataItemDomain = numpy.array(
        [[set() for _ in range(len(dataItemToIndex))] for _ in range(len(sourceToIndex))], dtype="object")
    dataItemDomain = numpy.array([set() for _ in range(len(dataItemToIndex))], dtype="object")

    for extractor in data:
        for source in data[extractor]:
            for triple in data[extractor][source]:
                dataItem = (triple[0], triple[1])
                value = triple[2]
                valueCube[extractorToIndex[extractor], sourceToIndex[source], dataItemToIndex[dataItem]] = value
                sourceDataItemDomain[sourceToIndex[source], dataItemToIndex[dataItem]].add(value)
                dataItemDomain[dataItemToIndex[dataItem]].add(value)

    print(multilayer(valueCube, sourceDataItemDomain, dataItemDomain, 100))


##################
# Error Checking #
##################

def calc_SqV(pVdEqualsVGivenX, IVdequalsV, dataItemDomain):
    # Calculates the difference between True (I) values and our (p) values
    total = 0
    for dataItemIndex in range(len(dataItemDomain)):
        for value in dataItemDomain[dataItemIndex]:
            diff = pVdEqualsVGivenX[dataItemIndex][value] - IVdequalsV[dataItemIndex][value]
            total += pow(diff, 2)

    return total


def calc_SqC(sourceDataItemDomain, pCwdvGivenXwdv, ICwdv):
    total = 0
    for sourceIndex in range(len(sourceDataItemDomain)):
        for dataItemIndex in range(len(sourceDataItemDomain[sourceIndex])):
            for value in sourceDataItemDomain[sourceIndex][dataItemIndex]:
                diff = pCwdvGivenXwdv[sourceIndex][dataItemIndex][value] - ICwdv[sourceIndex][dataItemIndex][value]
                total += pow(diff, 2)
    return total


def calc_SqA(A_calc, A_actual):
    total = 0
    for sourceIndex in range(len(A_calc)):
        diff = A_calc[sourceIndex].accuracy - A_actual[sourceIndex]
        total += pow(diff, 2)

    return total


# pVdEqualsVGivenX, dataItemDomain, sourceDataItemDomain, pCwdvGivenXwdv,
def error_Checking(valuesCube, A_calc):
    # Optional argument number 2 is the validation dataset

    # Accuracy Comparison 
    with open("sources.json", 'r') as inputFile:
        data = json.load(inputFile)
    return 0
    A_real = numpy.array([0 for _ in range(valuesCube.shape[1])])
    for s in data:
        A_real[int(s)] = int(data[s]["KBT"])

    SqA = calc_SqA(A_calc, A_real)
    print("Squared Error of Source Accuracies: " + str(SqA))

    # Extractor Comparison
    with open("")






if __name__ == "__main__":
    main()
