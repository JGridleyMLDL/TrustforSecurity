
#Put this line before the return statement at the end of the multilayer functions
error_Checking(valuesCube, sources, extractors)


##################
# Error Checking #
##################

def calc_SqV(pVdEqualsVGivenX, IVdequalsV, dataItemDomain):
    # Calculates the difference between True (I) values and our (p) values
    total = 0
    for dataItemIndex in range(len(dataItemDomain)):
        for value in dataItemDomain[dataItemIndex]:
            diff = pVdEqualsVGivenX[dataItemIndex][value] - \
                IVdequalsV[dataItemIndex][value]
            total += pow(diff, 2)

    return total


def calc_SqC(extractors, Ic):
    # If want to see all individually, then make a list and store in there
    total_p, total_r, count = 0, 0, 0
    for extrID in Ic.keys():
        actual_p = Ic[extrID]["precision"]
        our_p = extractors[int(extrID)].precision

        actual_r = Ic[extrID]["recall"]
        our_r = extractors[int(extrID)].recall

        total_p += pow(our_p - actual_p, 2)
        total_r += pow(our_r - actual_r, 2)

        count+=1

    avg_pError = total_p/count
    avg_rError = total_r/count
    return (avg_pError, avg_rError)


def calc_SqA(A_calc, A_actual):
    total = 0
    for sourceIndex in range(len(A_calc)):
        diff = A_calc[sourceIndex].accuracy - A_actual[sourceIndex]
        total += pow(diff, 2)

    return total


# pVdEqualsVGivenX, dataItemDomain, sourceDataItemDomain, pCwdvGivenXwdv,
def error_Checking(valuesCube, A_calc, Extractors):
    # Optional argument number 2 is the validation dataset

    # Accuracy Comparison
    with open("sources.json", 'r') as inputFile:
        data = json.load(inputFile)

    A_real = numpy.array([0 for _ in range(valuesCube.shape[1])])
    for s in data:
        A_real[int(s)] = int(data[s]["KBT"])


    # Value Comparison
    # Calculate the "true" triples from the source file

    # Call SqV to compare the file we got and the true triple.


    SqA = calc_SqA(A_calc, A_real)
    print("Squared Error of Source Accuracies: " + str(SqA))

    # Extractor Comparison
    with open("extractors.json", 'r') as extfile:
        data = json.load(extfile)

    iC = data
    SqC = calc_SqC(Extractors, iC)
    print("Squared Error of Extractors (p, r): " + str(SqC))

