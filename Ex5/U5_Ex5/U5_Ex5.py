from pyspark import SparkContext
from scipy.spatial import distance
import numpy as np
from pyspark.sql import *
from pyspark.sql.types import *

#spark = SparkSession \
#    .builder \
#    .appName("u4 ex5") \
#    .getOrCreate()

#sc = spark.sparkContext
#sc.setLogLevel("ERROR")
#sc.addPyFile("U5_Ex5.py")

def matrix_factorization(FactorizedMatrix_NxM, InitialMatrix_NxK, InitialMatrix_MxK, LatestFeaturesCount, Steps=5000, LearningRate=0.0002, Regularization=0.02):
    InitialMatrix_MxK = InitialMatrix_MxK.T
    for step in range(Steps):
        for i in range(len(FactorizedMatrix_NxM)):
            for j in range(len(FactorizedMatrix_NxM[i])):
                if FactorizedMatrix_NxM[i][j] > 0:
                    eij = FactorizedMatrix_NxM[i][j] - np.dot(InitialMatrix_NxK[i, :], InitialMatrix_MxK[:, j])
                    for k in range(LatestFeaturesCount):
                        InitialMatrix_NxK[i][k] = InitialMatrix_NxK[i][k] + LearningRate * (2 * eij * InitialMatrix_MxK[k][j] - Regularization * InitialMatrix_NxK[i][k])
                        InitialMatrix_MxK[k][j] = InitialMatrix_MxK[k][j] + LearningRate * (2 * eij * InitialMatrix_NxK[i][k] - Regularization * InitialMatrix_MxK[k][j])
        eR = np.dot(InitialMatrix_NxK, InitialMatrix_MxK)
        e = 0
        for i in range(len(FactorizedMatrix_NxM)):
            for j in range(len(FactorizedMatrix_NxM[i])):
                if FactorizedMatrix_NxM[i][j] > 0:
                    e = e + pow(FactorizedMatrix_NxM[i][j] - np.dot(InitialMatrix_NxK[i, :], InitialMatrix_MxK[:, j]), 2)
                    for k in range(LatestFeaturesCount):
                        e = e + (Regularization / 2) * (pow(InitialMatrix_NxK[i][k], 2) + pow(InitialMatrix_MxK[k][j], 2))

        print("Iteration: " + str(step) + " Error: " + str(e))
        if e < 0.001:
            break
    return InitialMatrix_NxK, InitialMatrix_MxK.T

if __name__ == '__main__':

    #UtilityMatrixRDD = sc.textFile('./recall_utility_matrix.txt').map(lambda line: line.split(','))

    UtilityMatrix = [
        [1, 0, 3, 0, 0, 5, 0, 0, 5, 0, 4, 0],
        [0, 0, 5, 4, 0, 0, 4, 0, 0, 2, 1, 3],
        [2, 4, 0, 1, 2, 0, 3, 0, 4, 3, 5, 0],
        [0, 2, 4, 0, 5, 0, 0, 4, 0, 0, 2, 0],
        [0, 0, 4, 3, 4, 2, 0, 0, 0, 0, 2, 5],
        [1, 0, 3, 0, 3, 0, 0, 2, 0, 0, 4, 0]
    ]

    UtilityMatrix = np.array(UtilityMatrix)

    print("Utility Matrix:")
    print(UtilityMatrix)

    Horizontal_N = len(UtilityMatrix)
    Vertical_M = len(UtilityMatrix[0])
    FeatureCount = 3

    InitialMatrix_P_NxK = np.random.rand(Horizontal_N, FeatureCount)
    InitialMatrix_Q_MxK = np.random.rand(Vertical_M, FeatureCount)

    P_Users_x_Features, Q_Items_x_Features = matrix_factorization(UtilityMatrix, InitialMatrix_P_NxK, InitialMatrix_Q_MxK, FeatureCount)

    New_Utility_Matrix = np.dot(P_Users_x_Features, Q_Items_x_Features.T)

    print("P_Items_x_Features:")
    print(P_Users_x_Features)
    print("Q_Users_x_Features:")
    print(Q_Items_x_Features.T)

    print("New_Utility_Matrix:")
    print(New_Utility_Matrix)
