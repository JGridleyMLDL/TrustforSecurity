import numpy as np
import math as m
import json


class DataPoint:
    def __init__(self, E, W, D, V):
        self.extractor = E
        self.value = V
        self.source = W
        self.data_item = D

    def calc_ewdv(self, e, w, d, v):
        # Checks if the triple is was extracted - THIS NEEDS ADJUSTING -
        if e in self.extractor and ((w, d, v) in e.triplets):
            return 1
        else:
            return 0


class Extractor:
    def __init__(self, data, R_e=0.8, Q_e=0.2):
        # data being a set() of triplet tuples containing all extracted information by the extractor over the dataset
        self.triplets = data
        self.R_e = R_e
        self.Q_e = Q_e


class InputData:
    def __init__(self, data):
        self.extractors = data['extractors']
        self.data_pairs = data['data_items']  # List of (d, v)
        self.sources = data['sources']
        self.data_items = []
        self.data_values = []
        for d in self.data_pairs:
            self.data_items.append(d[0])
            self.data_values.append(d[1])


'''
Class which will act as the container for an instance of this truth-discovery algorithm. This will maintain all hyperparameters along with default starting values
'''


class Model:
    def __init__(self, max_iter=100, A_w=0.5):
        self.A_w = A_w
        self.max_iter = max_iter

        self.theta = np.array(2)
    '''
    Analog for Algorithm 1 MultiLayer(X, t_max) from Knowledge Based Trust paper
    '''

    def multilayer(self):
        self.A = np.zeros(len(self.X))
        self.A += self.A_w

        # Test for if Z and theta converge, then return the value Loop - Convergence condition goes here
        itr = 0
        iteration_results = np.array()
        while itr <= self.max_iter:  # Change this to also check for convergence
            # Intermediary steps
            this_itr = np.array()
            for extractor in range(len(Extractors)):
                # Estimate C
                C = self.calc_Cwdv(DP)  # Percolate through other functions
                self.A_w = self.iterate_ahat(data)
                vote_count = self.calc_VCC_prime(data, DP)
                # Estimate V
                V = self.calc_Vd(data)
                # Estimate thetas
                theta1 = self.calc_A_w_hat(DP, data)
                theta2 = np.array(self.calc_P_e_hat(data),
                                  self.calc_R_e_hat(data))
                # Save the results
                self.A[extractor] = theta1
                this_itr.append((theta1, theta2))  # Make this more organized?
            iteration_results.append(this_itr)

    '''
    This block of functions are designated as those required to estiamte C
    '''

    def calc_Pre_e(self, e):
        # Presence vote for a triple that it extracts (Eq. 12)
        return m.log(e.R_e) - m.log(e.Q_e)

    def calc_Abs_e(self, e):
        # Absence vote for a triple that it does not extract (Eq. 13)
        return m.log(1 - e.R_e) - m.log(1 - e.Q_e)

    def calc_VCC(self, DP):
        # VCC calculates the for vote count (Eq. 14)
        # For each extractor, count the sum of presence and absence votes
        Pre_e, Abs_e = 0
        for e in DP.extractor:
            if DP.calc_ewdv(e, DP.source, DP.data_item, DP.value) == 1:
                Pre_e += self.calc_Pre_e(e)
            elif DP.calc_ewdv(e, DP.source, DP.data_item, DP.value):
                Abs_e += self.calc_Abs_e(e)
        return Pre_e + Abs_e

    # Modeled after equation 15 in the paper -- Returns P[C_{wdv} = 1 | X_{wdv}]
    def calc_Cwdv(self, DP):
        # Probability that w provides (d, v) given whether it was extracted
        result = calc_VCC(DP) + m.log((self.A_w) / (1 - self.A_w))              #Check if its supposed to be alpha
        result = 1 / (1 + (m.e ** -(result)))
        return result

INCORRENT - NEEDS ARGMAX ON PG 942


    # Modeled after equation 26 in the paper -- Returns \hat{a}^{t+1}

    def iterate_ahat(self, X):
        # Recalculates our assumption that a = p(Cwdv = 1)
        return self.calc_Vd(X) * self.A_w + (1 - self.calc_Vd(X))*(1 - self.A_w)

    # Modeled after equation 31 in the paper -- Returns VCC'(w, d, v)
    def calc_VCC_prime(self, X, DP):
        # Accounts for extraction confidence values
        result = 0
        for e in X.extractors:
            if DP.calc_ewdv(e, DP.source, DP.data_item, DP.value):
                result += self.calc_Pre_e(e)
            elif DP.calc_ewdv(e, DP.source, DP.data_item, DP.value):
                result += self.calc_Abs_e(e)
        return result

    '''
    This block of functions is designated as those required to estimate V
    '''

    # Modeled after equation 23 in the paper -- Returns VCV'(w, d, v)
    def calc_VCV_prime(self, DP):
        # Calculates the vote count for an extractor using weights now
        n = len(self.A)
        result = self.calc_Cwdv(DP) * m.log((n * self.A_w) / (1 - self.A_w))
        return result

    # Modeled after equation 24 in the paper -- Returns VCV'(d, v)
    def calc_VCV_prime_general(self, X, DP):
        # Sum of all vote counts for each source from the extractor with weights
        result = 0
        for w in X.sources:
            DP.source = w
            result += self.calc_VCV_prime(DP)
        return result

    # Modeled after equation 25 in the paper -- Returns P[V_d = v | X_d]
    def calc_Vd(self, X):
        # Probability that the extracted value is the true value.
        denom = 0
        for v in X.true_v:
            DP = DataPoint(None, None, X.data_item, v)
            denom += m.e ** (self.calc_VCV_prime_general(X, DP))
        return (m.e ** (self.calc_VCV_prime_general(X, DataPoint(None, None, X.data_item, X.value))) / denom)

    '''
    This block of functions is designed as those required to estimate Theta
    '''
    '''   Theta 1   '''

    # Modeled after equation 28 in the paper -- Returns \hat{A}_w^{t+1}
    def calc_A_w_hat(self, DP, X):
        # Calculating the accuracy of the web source
        num_val = 0
        den_val = 0
        for dataPoint in X.getData():
            if self.calc_Cwdv(dataPoint) > 1:
                num_val += self.calc_Cwdv(dataPoint) * self.calc_Vd(X)
                den_val += self.calc_Cwdv(dataPoint)
        return num_val / den_val

    '''   Theta 2   '''
    # Modeled after equation 32 in the paper -- Returns \hat{P}_e

    def calc_P_e_hat(self, X):
        # Calculating the precision of the extractor
        num_val = 0
        den_val = 0
        for dataPoint in X.getData():
            if dataPoint.calc_Xewdv() > 0:
                num_val += dataPoint.calc_Xewdv() * self.calc_Cwdv(dataPoint)
                den_val += dataPoint.calc_Xewdv()

    # Modeled after equation 33 in the paper -- Returns \hat{R}_e
    def calc_R_e_hat(self, X):
        # Calculating the recall of the extractor
        num_val, den_val = 0
        for dataPoint in X.getData():
            if dataPoint.calc_Xewdv() > 0:
                num_val += dataPoint.calc_Xewdv() * self.calc_Cwdv(dataPoint)
            den_val += self.calc_Cwdv(dataPoint)
        return num_val / den_val


if __name__ == "__main__":
    # Read input data and call the model
    with open("data.json", "r") as f:
        data = f.read()
    # Parsing the file
    json_data = json.loads(data)
