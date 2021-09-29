import sys
import json
import numpy as np


if len(sys.argv) != 2:
    print("Error - specify a data file.")


f = open(sys.argv[1], "r")
data = json.load(f)

Domain_map = dict()
source_map = dict()
Dataitem_indexes = dict()

num_dataitems = 0
num_sources = len(data["0"].keys())
num_extractors = len(data.keys())

for e in data.keys():

    for s in data[e].keys():

        for i in range(len(data[e][s])):

            triple = data[e][s][i]
            d = (triple[0], triple[1])
            v = triple[2]

            # Creating an index map that tells which data item is at which index
            if d not in Dataitem_indexes.keys():
                Dataitem_indexes[d] = num_dataitems
                num_dataitems += 1

            # Creating the Domain map (converted to list later)
            if d in Domain_map:
                Domain_map[d].add(v)
            else:
                Domain_map[d] = {v}

            # Source Map (converted to list format later)
            if s in source_map.keys():
                if d in source_map[s].keys():
                    source_map[s][d].add(v)
                else:
                    source_map[s][d] = {v}

            else:
                source_map[s] = {d: {v}}

# Converting the domain_map and source_map to lists.
Domain_list = [set() for i in range(num_dataitems)]
for d in Domain_map.keys():
    index = Dataitem_indexes[d]
    Domain_list[index] = Domain_map[d]

Source_list = [[set() for i in range(num_dataitems)]] * num_sources
for s in source_map.keys():
    for d in source_map[s].keys():
        index = Dataitem_indexes[d]
        Source_list[int(s)][index] = source_map[s][d]


# Creating the matrix cube
# Matrix is initialized to all zeros for "value" and "confidence" values
Matrix3D = np.zeros((num_extractors, num_sources, num_dataitems, 2))


# Creating the value cube of+ the data.
ValueMatrixCube = np.zeros((num_extractors, num_sources, num_dataitems))
for e in data.keys():
    for s in data[e].keys():
        for i in range(len(data[e][s])):
            triple = data[e][s][i]
            d = (triple[0], triple[1])
            v = triple[2]
            index = Dataitem_indexes[d]
            ValueMatrixCube[int(e)][int(s)][index] = v

print(ValueMatrixCube)

print(Domain_list)
print(Source_list)
