# This line goes right before the return statement in the multilayer function
error_Checking(valuesCube, sources)






##################
# Error Checking #
##################

def calc_SqV(pVdEqualsVGivenX, IVdequalsV, dataItemDomain):
    # Calculates the difference between True (I) values and our (p) values
    total = 0
    count = 0
    for dataItemIndex in range(len(dataItemDomain)):
        for value in dataItemDomain[dataItemIndex]:
            diff = pVdEqualsVGivenX[dataItemIndex][value] - IVdequalsV[dataItemIndex][value]
            total += pow(diff, 2)
            count += 1

    return total / count


def calc_SqC(sourceDataItemDomain, pCwdvGivenXwdv, ICwdv):
    total = 0
    count = 0
    for sourceIndex in range(len(sourceDataItemDomain)):
        for dataItemIndex in range(len(sourceDataItemDomain[sourceIndex])):
            for value in sourceDataItemDomain[sourceIndex][dataItemIndex]:
                diff = pCwdvGivenXwdv[sourceIndex][dataItemIndex][value] - ICwdv[sourceIndex][dataItemIndex][value]
                total += pow(diff, 2)
                count += 1
    return total / count


def calc_SqA(A_calc, A_actual):
    total = 0
    count = 0
    for sourceIndex in range(len(A_calc)):
        diff = A_calc[sourceIndex].accuracy - A_actual[sourceIndex]
        total += pow(diff, 2)
        count += 1

    return total / count


# pVdEqualsVGivenX, dataItemDomain, sourceDataItemDomain, pCwdvGivenXwdv,
def error_Checking(valuesCube, A_calc):
    # Optional argument number 2 is the validation dataset
    with open("sources.json", 'r') as inputFile:
        data = json.load(inputFile)

    A_real = numpy.array([0 for _ in range(valuesCube.shape[1])])
    for s in data:
        A_real[int(s)] = int(data[s]["KBT"])

    SqA = calc_SqA(A_calc, A_real)
    print("Squared Error of Source Accuracies: " + str(SqA))
