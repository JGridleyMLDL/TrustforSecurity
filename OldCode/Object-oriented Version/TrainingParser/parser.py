import json

'''

Function which is designed to parse and serialize sentences from a .txt file for training.

file_name -> The name of the file which is being parsed

'''
def getSentences(file_name):
    # return object
    sentences = []
    sentence_positions = []

    with open(file_name, "r") as f:
        
        current_position_start = 0
        current_position_end = 0
        for line in f:
            current_position_start = current_position_end
            current_position_end = current_position_start + len(line)
            line = line.strip()
            sent = []
            # Ensure we are operating on a line with content in it
            if line != "":
                line = line.split()
                for word in line:
                    # Logic tree which is designed to separate certain characters but preserve them in the return object
                    if word.find(".") != -1:
                        sent.append(word[:word.find(".")]) 
                        sent.append(word[word.find(".")])
                        if word.find(".") != len(word) - 1: sent.append(word[word.find(".") + 1:])
                    elif word.find(",") != -1:
                        sent.append(word[:word.find(",")]) 
                        sent.append(word[word.find(",")])
                        if word.find(",") != len(word) - 1: sent.append(word[word.find(",") + 1:])
                    elif word.find("?") != -1:
                        sent.append(word[:word.find("?")]) 
                        sent.append(word[word.find("?")])
                        if word.find("?") != len(word) - 1: sent.append(word[word.find("?") + 1:])
                    elif word.find("!") != -1:
                        sent.append(word[:word.find("!")]) 
                        sent.append(word[word.find("!")])
                        if word.find("!") != len(word) - 1: sent.append(word[word.find("!") + 1:])
                    else:
                        sent.append(word)
                sentence_positions.append((current_position_start, current_position_end))
                sentences.append(sent)
        f.close()
    return sentences, sentence_positions

def getVerticies(annotationFileName, sentences):
    verticies = []

    with open(annotationFileName, "r") as f:
        for line in f:
            if line[0] != "T":
                continue
            vertex = {}
            # verticies.append(line.strip())
            line = line.split("\t")
            vertex['old_id'] = line[0].strip()
            vertex['type'] = line[1].split()[0].strip()
            vertex['name'] = line[2].strip().replace('.', '').replace(',', '').replace('!', '').replace('?', '')

            for i in range(len(sentences[1])):
                if int(line[1].split()[1]) >= sentences[1][i][0] and int(line[1].split()[2]) <= sentences[1][i][1]:
                    vertex['sent_id'] = i
            if 'sent_id' not in vertex.keys(): vertex['sent_id'] = None
            if vertex['sent_id'] is None: vertex['pos'] = []
            else: 
                if len(vertex['name'].split()) != 1:
                    vertex['pos'] = []
                    try:
                        vertex['pos'].append(sentences[0][vertex['sent_id']].index(vertex['name'].split()[0]))
                        vertex['pos'].append(sentences[0][vertex['sent_id']].index(vertex['name'].split()[-1]))
                    except ValueError:
                        vertex['pos'] = []
                else:
                    try:
                        vertex['pos'] = [sentences[0][vertex['sent_id']].index(vertex['name'])]
                    except ValueError:
                        vertex['pos'] = []

            verticies.append(vertex)
        
        f.close()

    return verticies

def getRelations(annotationFileName, verticies, sentences):
    labels = []
    with open("rel_info.json", 'r') as f:
        relDict = json.load(f)
        f.close()
    
    with open(annotationFileName, "r") as f:
        for line in f:
            if line[0] != "R":
                continue
            relationship = {}

            line = line.strip()
            line = line.split('\t')
            relationship['old_id'] = line[0]
            relationship['r'] = line[1].split()[0].lower()
            relationship['r'] = list(relDict.keys())[list(relDict.values()).index(relationship['r'])]
            relationship['h'] = line[1].split()[1].split(":")[1]
            relationship['t'] = line[1].split()[2].split(":")[1]

            for i in range(len(verticies)):
                if verticies[i]['old_id'] == relationship['h']: relationship['h'] = i
                if verticies[i]['old_id'] == relationship['t']: relationship['t'] = i

            relationship['evidence'] = []
            startSent = verticies[relationship['h']]['sent_id']
            endSent = verticies[relationship['t']]['sent_id']
            if startSent is not None and endSent is not None:
                for val in range(startSent, endSent + 1):
                    relationship['evidence'].append(val)


            labels.append(relationship)
    return labels

def parseTrainDoc(filename, annotationName, trainingFile=None):
    document = {}
    document['sents'] = getSentences(filename)
    document['title'] = filename

def genRelInfo():
    i = 1
    relations = {}
    while True:
        try:
            inp = input("enter relationship:\n")
            relations[f"P{i}"] = inp.lower().strip()
            i += 1
        except KeyboardInterrupt:
            break
    
    jsonOUT = json.dumps(relations)
    with open("rel_info.json", "w") as f:
        f.write(jsonOUT)
        f.close()

def trainingParse(filename, annFilename, existingTrainingFile=None):
    sentences = getSentences(filename)
    verticies = getVerticies(annFilename, sentences)
    relations = getRelations(annFilename, verticies, sentences)
    outObj = {}
    outObj['vertexSet'] = verticies
    outObj['labels'] = relations
    outObj['title'] = filename.split(".")[:-1]
    outObj['sents'] = sentences[0]

    if existingTrainingFile is not None:
        with open(existingTrainingFile, 'w') as f:
            js = json.load(f)
            js.append(outObj)
            json.dump(js, f)
            f.close()

    else:
        with open("outputs/train.json", 'w') as f:
            outObj = [outObj]
            json.dump(outObj, f)
            f.close()

    print("Saved data")




if __name__ == "__main__":
    annFilename = "inputs/201407CrowdStrikeDeepPanda.ann"
    filename = "inputs/201407CrowdStrikeDeepPanda.txt"
    
    trainingParse(filename, annFilename)