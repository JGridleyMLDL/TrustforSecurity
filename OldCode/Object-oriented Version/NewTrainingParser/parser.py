import json
import nltk
from pprint import pprint

# Download the punkt nlkt package if not already installed
nltk.download('punkt')

# Parse the brat .ann file into a python dictonary for further work
def get_brat_dict(ann_file):
    with open(ann_file, 'r') as f:
        ret_dict ={} 
        for line in f:
            line = line.split()
            # Sets the key to the brat ID (T# or R#)
            ret_dict[line[0]] = line[1:]
        f.close()

    return ret_dict

# Generate a list of all sentences in a given document using NLTK
def get_sentences(text_file):
    with open(text_file, 'r') as f:
        doc = ''

        for line in f:
            doc += line

        nltk_sentences = nltk.sent_tokenize(doc)

        sentences = []
        for s in nltk_sentences:
            s = ''.join(s)
            sentences.append(s)

        f.close()

    return sentences 

# Convert raw brat dictionary into the proper format for the DocRED model
def translate_verticies(raw_verticies):
    vertex_list = []
    for key, val in raw_verticies.items():
        tmp_dict = {}
        tmp_dict['name'] = ' '.join(val[3:])
        if tmp_dict['name'].find(',') != -1: continue
        tmp_dict['brat_id'] = key
        tmp_dict['pos'] = val[1:3]
        for i in range(len(tmp_dict['pos'])):
            if tmp_dict['pos'][i].find(";") != -1:
                tmp_dict['pos'][i] = tmp_dict['pos'][i].split(";")[-1]
            tmp_dict['pos'][i] = int(tmp_dict['pos'][i])
        tmp_dict['type'] = val[0]
        vertex_list.append(tmp_dict)
    return vertex_list

# Find the pos tuple and sent_id for the set of verticies
def get_sent_id_and_pos(raw_sentences, brat_dict):
    verticies = {} 
    for key, val in brat_dict.items():
        if key.find("T") != -1: verticies[key] = brat_dict[key]

    verticies = translate_verticies(verticies)
    verticies.sort(key=lambda x: x['pos'][0]) 
        
    i = 0
    j = 0
    # Loop to determine the sent_id for all given verticies
    while True:
        if i == len(raw_sentences) or j == len(verticies): break
        if raw_sentences[i].find(verticies[j]['name']) != -1:
            verticies[j]['sent_id'] = i
            j += 1
        else:
            i += 1
    remove_idx = []
    for j in range(len(verticies)):
        # Currently removes elements which are not detected in the sentences
        # TODO -- Fix sentence detection for really really long names
        if 'sent_id' not in verticies[j].keys(): 
            remove_idx.append(j)
            continue
        sent = raw_sentences[verticies[j]['sent_id']]
        sent = sent.replace(".", '').replace('(', '').replace(')', '').replace(",", '').replace("!", '').replace(":", '').replace(";", '').replace("?", '').split()
        verticies[j]['name'] = verticies[j]['name'].split()
        name_start_idx = verticies[j]['name'][0]
        name_start_idx = sent.index(name_start_idx)
        if name_start_idx == -1: raise ValueError("Wrong sentence ID")
        else:
            if verticies[j]['name'] == sent[name_start_idx:name_start_idx + len(verticies[j]['name'])]:
                verticies[j]['pos'] = [name_start_idx, name_start_idx + len(verticies[j]['name'])]
        verticies[j]['name'] = ' '.join(verticies[j]['name'])

    # Delete recorded list indicies
    remove_idx.reverse()
    for i in remove_idx:
        verticies.pop(i)
    return verticies

# Remove \n from extracted sentences for sents
def clean_sentences(raw_sentences):
    sentences = []
    for s in raw_sentences:
        s = s.replace('\n', '')
        sentences.append(s)

    return sentences

# Same as translate_verticies but for the relations/labels
def translate_relations(raw_labels, vertexSet):
    relations = []
    for key, val in raw_labels.items():
        tmp_dict = {}
        # val = val.split()
        brat_head = val[1].split(":")[-1]
        brat_tail = val[2].split(":")[-1]
        brat_relation = val[0].lower()
        tmp_dict['brat_id'] = key
        for i in range(len(vertexSet)):
            for j in range(len(vertexSet[i])):
                if vertexSet[i][j]['brat_id'] == brat_head: tmp_dict['h'] = i
                if vertexSet[i][j]['brat_id'] == brat_tail: tmp_dict['t'] = i
        with open("rel_to_id.json") as f:
            relations_map = json.load(f)
            f.close()
        tmp_dict['r'] = relations_map[brat_relation]
        tmp_dict['evidence'] = [vertexSet[tmp_dict['h']][0]['sent_id'], vertexSet[tmp_dict['t']][0]['sent_id']]

        relations.append(tmp_dict)
    return relations


# Select only things with brat ID prefix "R" for the translate_relations function
def get_labels(brat_dictionary, vertexSet):
    raw_labels = {}
    for key, val in brat_dictionary.items():
        if key.find("R") != -1: raw_labels[key] = brat_dictionary[key]

    labels = translate_relations(raw_labels, vertexSet)
    return labels

# Main code runner function for parsing a given file provided the filename 
def construct_document_json(filename):
    document = {}
    ann_file = filename + ".ann"
    rdict = get_brat_dict(ann_file)

    raw_sentences = get_sentences(filename + '.txt')
    sentences = clean_sentences(raw_sentences)
    document['sents'] = sentences
    document['title'] = filename[7:]
    verticies = get_sent_id_and_pos(raw_sentences, rdict)
    document['vertexSet'] = []
    for v in verticies:
        appended = False
        for i in range(len(document['vertexSet'])):
            if document['vertexSet'][i][0]['name'] == v['name']:
                document['vertexSet'][i].append(v)
                appended = True
        if not appended:
            document['vertexSet'].append([v])
    document['labels'] = get_labels(rdict, document['vertexSet'])
    pprint(document['labels'])
    with open("training.json", 'w') as f:
        json.dump(document, f)
        f.close()

if __name__ == "__main__":
    # filename = "inputs/shadows-in-the-cloud"
    filename = 'inputs/201407CrowdStrikeDeepPanda'
    construct_document_json(filename)
