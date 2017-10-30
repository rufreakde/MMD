""" IMMD-2017: Problem Set 1 Exercise 3 """

from __future__ import print_function
import sys
import numpy as np
from pyspark.sql import SparkSession

# Function parseVector turns a text line with numbers into a numpy-vector
def parseVector(line):
    return np.array([float(x) for x in line.split(' ')])


def closestPoint(p, centers):
    bestIndex = 0
    closest = float("+inf")
    for i in range(len(centers)):
        tempDist = np.sum((p - centers[i]) ** 2)
        if tempDist < closest:
            closest = tempDist
            bestIndex = i
    return bestIndex


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: kmeans <file> <k> <convergeDist>", file=sys.stderr)
        exit(-1)

    print("""WARN: This is a naive implementation of KMeans Clustering and is given
       as an example! Please refer to examples/src/main/python/ml/kmeans_example.py for an
       example on how to use ML's KMeans implementation.""", file=sys.stderr)

    spark = SparkSession \
        .builder \
        .appName("PythonKMeans") \
        .getOrCreate()

    # Get the input parameters
    lines = spark.read.text(sys.argv[1]).rdd.map(lambda r: r[0])
    data = lines.map(parseVector).cache() # apply parseVector to every line and cache created RDD (with numpy-vectors as elements) in memory
    K = int(sys.argv[2])
    convergeDist = float(sys.argv[3])

    kPoints = data.takeSample(False, K, 1) # spark action takeSample takes K records and returns them to the driver --> these are the random centroids
    tempDist = 1.0

    while tempDist > convergeDist:
        # Place each point in the cluster with the nearest centroid
        closest = data.map(
            lambda p: (closestPoint(p, kPoints), (p, 1)))
        # Update the locations of centroids of the k clusters
        pointStats = closest.reduceByKey(
            lambda p1_c1, p2_c2: (p1_c1[0] + p2_c2[0], p1_c1[1] + p2_c2[1])) # --> returns for every cluster: (sum of points in cluster, number of points in cluster)
        newPoints = pointStats.map(
            lambda st: (st[0], st[1][0] / st[1][1])).collect() # compute each new centroid by dividing the sum of points in a cluster by the number of points in the cluster.

        # Calculate sum of squared euclidean distance between old and new centroids
        tempDist = sum(np.sum((kPoints[iK] - p) ** 2) for (iK, p) in newPoints)

        # Assign new centroids for each cluster
        for (iK, p) in newPoints:
            kPoints[iK] = p

    print("Final centers: " + str(kPoints))

    spark.stop()
