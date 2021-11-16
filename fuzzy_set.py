import numpy as np
import pandas as pd


class FuzzySet:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(self.path)
        membership = []
        non_membership = []
        for i in range(self.df.shape[1]):
            if i % 2 == 0:
                membership.append(self.df.iloc[:, i].to_numpy())
            else:
                non_membership.append(self.df.iloc[:, i].to_numpy())
        self.membership = membership
        self.non_membership = non_membership

    def similarity(self, other):
        assert isinstance(other, FuzzySet)
        numerator = 0
        denominator = 0
        for i in range(len(self.membership)):
            numerator += np.dot(self.membership[i], other.membership[i])
            numerator += np.dot(self.non_membership[i], other.non_membership[i])

            denominator += max(np.dot(self.membership[i], self.membership[i]), np.dot(other.membership[i], other.membership[i]))
            denominator += max(np.dot(self.non_membership[i], self.non_membership[i]), np.dot(other.non_membership[i], other.non_membership[i]))
        return numerator/denominator

    def weighted_similarity(self, other, weights):
        assert isinstance(other, FuzzySet)
        numerator = 0
        denominator = 0
        for i in range(len(self.membership)):
            numerator += weights[i] * np.dot(self.membership[i], other.membership[i])
            numerator += weights[i] * np.dot(self.non_membership[i], other.non_membership[i])

            denominator += max(np.dot(self.membership[i], self.membership[i]), np.dot(other.membership[i], other.membership[i]))
            denominator += max(np.dot(self.non_membership[i], self.non_membership[i]), np.dot(other.non_membership[i], other.non_membership[i]))
        return numerator/denominator/np.sum(weights)


if __name__ == '__main__':
    A = FuzzySet("data\set_1.csv")
    print(A.membership)
    print(A.non_membership)
    B = FuzzySet("data\set_2.csv")
    print(B.membership)
    print(B.non_membership)
    print(A.similarity(B))
    print(A.weighted_similarity(B, weights=[0.5, 0.6, 0.8]))
    M = FuzzySet("data\disease_1_M.csv")
    P1 = FuzzySet("data\disease_1_P1.csv")
    print(P1.membership)
    print(P1.non_membership)
    print(P1.similarity(M))
