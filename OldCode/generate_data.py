import json
import sys
import numpy

#extractors = {0: {"precision": 0.5, "recall": 0.5}}
#sources = {0: {"KBT": 0.5, "triples": [[0,0,0], [0,1,None]]}}
#Correct triples have a value of 0, incorrect triples have a value of 1 through 25

#format = {0: {0: [], 1: [], 2: []} }

def generateTriples(quantity):
    relationQuantity = round(numpy.sqrt(quantity))
    triples = []
    i = 0
    while i * relationQuantity < quantity:
        for j in range(int(relationQuantity)):
            if i * relationQuantity + j >= quantity:
                break
            triples.append([i, j, 0])
        i += 1
    return triples

#Generates a source with [minimumNumberOfTriples, maximumNumberOfTriples) triples and a KBT of [0.0, 1.0] uniformly
#Randomly shuffles allTriples
def generateSource(allTriples, minimumNumberOfTriples, maximumNumberOfTriples):
    triples = numpy.random.default_rng().choice(allTriples, numpy.random.default_rng().integers(minimumNumberOfTriples, maximumNumberOfTriples), replace = False, shuffle = False).tolist()
    incorrectTripleCount = numpy.random.default_rng().integers(0, len(triples) + 1)
    for i in range(incorrectTripleCount):
        triples[i][2] = int(numpy.random.default_rng().integers(1, 26))
    numpy.random.default_rng().shuffle(triples)
    return {"KBT": (len(triples) - incorrectTripleCount)/len(triples), "triples": triples}

#Generates an extractor with a precision and recall of [0.1, 1.0) uniformly
def generateExtractor():
    return {"precision": numpy.random.default_rng().uniform(0.1, 1.0), "recall": numpy.random.default_rng().uniform(0.1, 1.0)}

def extract(extractor, source, allTriples):
    relevantCount = round(extractor["recall"] * len(source["triples"]))
    irrelevantCount = min(round((1/extractor["precision"] - 1) * relevantCount), len(source["triples"]) - relevantCount) #Messes up precision to an unknown degree
    extractedTriples = numpy.random.default_rng().choice(source["triples"], relevantCount + irrelevantCount, replace = False, shuffle = False).tolist()
    for tripleIndex in range(irrelevantCount):
        extractedTriples[tripleIndex][2] = int(numpy.random.default_rng().integers(1, 26))
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
        sources[i] = generateSource(triples, 1, 101) #Controls how many triples can be in a source
    print("Completed!\n")

    print("Generating extractors...")
    for i in range(int(sys.argv[3])):
        extractors[i] = generateExtractor()
    print("Completed!\n")

    print("Extracting triples from sources...")
    for extractorID in range(int(sys.argv[3])):
        tmp = {}
        for sourceID in range(int(sys.argv[2])):
            tmp[sourceID] = extract(extractors[extractorID], sources[sourceID], triples)
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
