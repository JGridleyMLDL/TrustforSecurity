class DataMatrix:

    # Imagine having a 3 Dimensional Matrix for all of the data
    Matrix3D = numpy.zeros(Extractors, Sources, DataItems)
        #Needs to be accessible for sources and extractors --> Can iterate by i, j, or k



    #Need modifing functions for while reading in JSON data




# Function or class that keeps track of extractor accuracies. 

class Extractors:
    #Idea is a 3d matrix with accuracies, precision, recall, Q
    extractor_Accuracies = numpy(extractor_id_rows, accuracies_as_columns)

    def New_Accuracy_Prediction(extractor_id, accuracy):
        #creates a new columns for this iteration's accuracies 



Matrix3D = numpy.zeros(Extractors, Sources, DataItems)
f = open("data.json", "r")
data = json.load(f)

for e in range(data.keys()):
    for s in range(e.keys()):
        for i in range(len(data[e][s])):
            #data_pair = (data[s][e][i][0], (data[s][e][i][1], data[s][e][i][2]))
            Matrix3D[e][s][i] = (0, 0)
