from pyspark import SparkContext
from scipy.spatial import distance
import numpy as np
from pyspark.sql import *
from pyspark.sql.types import *
from pyspark.mllib.recommendation import Rating
from pyspark.mllib.recommendation import ALS

def even(x): return x[0] % 2 == 0
def odd(x): return not even(x)

spark = SparkSession \
    .builder \
    .appName("u5 ex4") \
    .getOrCreate()

sc = spark.sparkContext
sc.addPyFile("U5_Ex4.py")

if __name__ == '__main__':

    MovielensDataset = sc.textFile('./movielens.txt').map(lambda line: line.split()) \
        .map(lambda element: Rating(int(element[0]), int(element[1]), int(element[2])))

    TrainingData, TestData = MovielensDataset.randomSplit([0.50000000, 0.5000000], 10)

    TrainingModel = ALS.train(TrainingData, 10, 5)

    #just ussed once to generate serialized testdata!
    #TrainingModel.save(sc, "./serialized/")

    # Evaluate the model on training data
    testdata = TestData.map(lambda p: (p[0], p[1]))
    predictions = TrainingModel.predictAll(testdata).map(lambda r: ((r[0], r[1]), r[2]))
    ratesAndPreds = TestData.map(lambda r: ((r[0], r[1]), r[2])).join(predictions)
    MSE = ratesAndPreds.map(lambda r: (r[1][0] - r[1][1])**2).mean()
    print("Mean Squared Error = " + str(MSE))
    print(ratesAndPreds.take(5))