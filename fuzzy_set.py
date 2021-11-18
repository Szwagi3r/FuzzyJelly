import numpy as np
import pandas as pd


class Diagnosis:
    def __init__(self, patients, diseases, results_table, diagnosis, method):
        self.patients = patients
        self.diseases = diseases
        self.results_table = results_table
        self.diagnosis = diagnosis
        self.method = method


class FuzzySet:
    def __init__(self, path, rownames=True):
        self.path = path
        if rownames:
            self.df = pd.read_csv(self.path, index_col=0)
        else:
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
        df2 = []
        for i in range(len(membership[0])):
            new_obs = []
            for j in range(len(membership)):
                new_obs.append([membership[j][i], non_membership[j][i]])
            df2.append(new_obs)
        df_compressed = pd.DataFrame(df2)
        df_compressed.columns = [self.df.columns[2*i] for i in range(len(membership))]
        df_compressed.index = self.df.index
        self.df_compressed = df_compressed

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

    def distance_diagnosis(self, patients, dist_type="euclidean"):
        def distance(disease, patient, dist_type):
            result = 0
            if dist_type == "euclidean":
                for i in range(len(patient)):
                    result += (disease[i][0] - patient[i][0])**2+(disease[i][1] - patient[i][1])**2+(disease[i][0] - patient[i][0] + disease[i][1] - patient[i][1])**2
                return np.sqrt(result)
            if dist_type == "absolute":
                for i in range(len(patient)):
                    result += (disease[i][0] - patient[i][0])**2+(disease[i][1] - patient[i][1])**2+(disease[i][0] - patient[i][0] + disease[i][1] - patient[i][1])**2
                return np.sqrt(result)

        if dist_type not in ["euclidean", "absolute"]:
            print("Wrong distance type, using euclidean instead.")
            dist_type = "euclidean"
        distances = []
        for P_id in range(patients.df_compressed.shape[0]):
            patient_distances = []
            for D_id in range(self.df_compressed.shape[1]):
                patient = patients.df_compressed.iloc[P_id, :]
                disease = self.df_compressed.iloc[:, D_id]
                patient_distances.append(distance(disease, patient, dist_type))
            distances.append(patient_distances)
        df_distances = pd.DataFrame(distances)
        df_distances.columns = self.df_compressed.columns
        df_distances.index = patients.df_compressed.index
        diagnosis = []
        for P_id in range(df_distances.shape[0]):
            diagnosis.append([df_distances.index[P_id], df_distances.columns[np.argmin(df_distances.iloc[P_id, :])]])
        return Diagnosis(patients.df_compressed, self.df_compressed, df_distances, pd.DataFrame(diagnosis, columns=["patient", "disease"]), method=dist_type+" distance")

    def similarity_diagnosis(self, patients_paths):
        result = []
        ids = []
        for path in patients_paths:
            P = FuzzySet(path)
            result.append([P.df_compressed.index[0], self.similarity(P)])
            ids.append(P.df_compressed.index[0])
        return pd.DataFrame(result, columns=["patient", "similarity"])


if __name__ == '__main__':
    A = FuzzySet("data/distance/patients.csv")
    B = FuzzySet("data/distance/diseases.csv")
    d = B.distance_diagnosis(A, dist_type="e")
    print(d.diagnosis)
    print(d.method)

    M = FuzzySet("data\similarity\dengue.csv")
    print(M.df_compressed)
    patients_paths = ["data\similarity\P" + str(i+1) + ".csv" for i in range(15)]
    print(patients_paths)
    print(M.similarity_diagnosis(patients_paths))
