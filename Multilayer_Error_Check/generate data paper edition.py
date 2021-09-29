import json
import sys
import numpy
import copy

#extractors = {0: {"precision": 0.5, "recall": 0.5}}
#sources = {0: {"KBT": 0.5, "triples": [[0,0,0], [0,1,None]]}}
#Correct triples have a value of 0, incorrect triples have a value of 1 through 25

#format = {0: {0: [], 1: [], 2: []} }

def generateTriples(quantity):
    triples = []
    for i in range(1, quantity + 1):
        triples.append([i, i, i])
    return triples

#Randomly shuffles triples
def generateSource(allTriples, accuracy = 0.7):
    triples = copy.deepcopy(allTriples)
    numpy.random.default_rng().shuffle(triples)
    for triple in triples:
        if numpy.random.default_rng().integers(0, 100)/100 > accuracy:
            tmp = numpy.random.default_rng().integers(0, 2)
            if tmp == 0:
                triple[0] = 0
            elif tmp == 1:
                triple[1] = 0
            else:
                triple[2] = 0

    return {"KBT": 0.7, "triples": triples}

#Generates an extractor with a precision and recall of [0.1, 1.0) uniformly
def generateExtractor():
    return {"precision": 0.5, "recall": 0.5}

def extract(extractor, source):
    extractedTriples = []
    for triple in source["triples"]:
        if numpy.random.default_rng().integers(0, 100)/100 > extractor["recall"]:
            extractedTriples.append(copy.deepcopy(triple))
            for i in range(len(extractedTriples[-1])):
                if numpy.random.default_rng().integers(0, 100)/100 > numpy.cbrt(extractor["precision"]):
                    extractedTriples[-1][i] = -1
    numpy.random.default_rng().shuffle(extractedTriples)
    return extractedTriples

def main():
    if len(sys.argv) != 4:
        print("Usage:", sys.argv[0], "[number of triples] [number of sources] [number of extractors]")
        exit()

    triples = []
    sources = {}
    extractors = {}
    multilayerinput = {}

    print("Generating triples...")
    triples = generateTriples(int(sys.argv[1]))
    print("Completed!\n")

    print("Generating sources...")
    for i in range(int(sys.argv[2])):
        sources[i] = generateSource(triples)
    print("Completed!\n")

    print("Generating extractors...")
    for i in range(int(sys.argv[3])):
        extractors[i] = generateExtractor()
    print("Completed!\n")

    print("Extracting triples from sources...")
    for extractorID in range(int(sys.argv[3])):
        tmp = {}
        for sourceID in range(int(sys.argv[2])):
            if numpy.random.default_rng().integers(0, 100)/100 > 0.5:
                tmp[sourceID] = extract(extractors[extractorID], sources[sourceID])
        multilayerinput[extractorID] = tmp
    print("Completed!\n")

    print("Writing to files...")
    with open("triples.json", "w") as triplesFile, open("sources.json", "w") as sourcesFile, open("extractors.json", "w") as extractorsFile, open("multilayerinput.json", "w") as multilayerInputFile:
        json.dump(triples, triplesFile, indent = 2)
        json.dump(sources, sourcesFile, indent = 2)
        json.dump(extractors, extractorsFile, indent = 2)
        json.dump(multilayerinput, multilayerInputFile, indent = 2)
    print("Completed!")

if __name__ == "__main__":
    main()
