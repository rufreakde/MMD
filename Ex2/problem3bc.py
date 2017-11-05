#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
The K-means algorithm written from scratch against PySpark. In practice,
one may prefer to use the KMeans algorithm in MLlib, as shown in
examples/src/main/python/mllib/kmeans.py.

This example requires NumPy (http://www.numpy.org/)

You can install Numpy in the VM by running the following command:
    pip3 install numpy

This example required Matplotlib to visualize the data. Matplotlib is installed
with python3 but the Tkinter module (a dependency from Matplotlib) is not installed
by default on Ubuntu distributions.

You can install python3-tinker by running the following command:
    sudo apt-get install python3-tk

"""

import sys

import numpy as np
from pyspark import SparkContext
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from math import sqrt


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


def distanceCentroidsMoved(oldCentroids, newCentroids):
    sum = 0.0
    for index in range(len(oldCentroids)):
        sum += np.sum((oldCentroids[index] - newCentroids[index]) ** 2)
    return sum


def generateData(N, k):
    """ Generates N 2D points in k clusters
        From http://datasciencelab.wordpress.com/2013/12/12/clustering-with-k-means-in-python/
    """
    n = float(N) / k
    X = []
    for i in range(k):
        c = (random.uniform(-1, 1), random.uniform(-1, 1))
        s = random.uniform(0.05, 0.5)
        x = []
        while len(x) < n:
            a, b = np.array([np.random.normal(c[0], s), np.random.normal(c[1], s)])
            # Continue drawing points from the distribution in the range [-1,1]
            if abs(a) < 1 and abs(b) < 1:
                x.append([a, b])
        X.extend(x)
    X = np.array(X)[:N]
    return X


def visualizeClusters(data, centroids, iteration):
    """
    Function used to plot the cluster centroids and data.
    """
    plt.clf()
    plt.gcf().clear()

    colors = cm.rainbow(np.linspace(0, 1, len(centroids)))

    plt.title("Iteration: %d" % iteration)

    for p in data:
        index = p[0]
        color = colors[index]
        x, y = p[1][0]
        plt.scatter(x, y, color=color)

    for c in centroids:
        plt.scatter(c[0], c[1], color="black", marker="*", s=60)

    plt.pause(0.5)

def bcv(centroids):
    sum = 0
    for index, centroid in enumerate(centroids):
        if index+1 < len(centroids):
            for nextCentroid in range(index+1, len(centroids)):
                sum += sqrt((centroid[0] - centroids[nextCentroid][0])**2 + (centroid[1] - centroids[nextCentroid][1])**2)**2
    return sum

def wcv(closest, centroids):
    value = closest.map(lambda point: error(point, centroids)).reduce(lambda x, y: x + y)
    return value

def error(point, centroids):
    currentCentroid = centroids[point[0]]
    pointCoordinates = point[1][0]
    pointError = sqrt((pointCoordinates[0] - currentCentroid[0])**2 + (pointCoordinates[1] - currentCentroid[1])**2)**2
    return pointError

def sse(closest, centroids):
    value = closest.map(lambda point: error(point, centroids)).reduce(lambda x, y: x + y)
    return value


def kmeans(numberCluster, data, convergeDist):
    centroids = data.takeSample(False, numberCluster, 1)
    newCentroids = centroids[:]  # creates a copy
    maxNumberIterations = 10
    counter = 0
    tempDist = 2 * convergeDist
    while tempDist > convergeDist or counter > maxNumberIterations:
        print("\n### Iteration#: %d" % (counter))
        counter += 1

        closest = data.map(lambda p: (closestPoint(p, centroids), (p, 1)))

        #visualizeClusters(closest.collect(), centroids, counter)  # plot

        for cIndex in range(numberCluster):
            closestOneCluster = closest.filter(lambda d: d[0] == cIndex).map(lambda d: d[1])
            #print("Cluster with index %d has %d points" % (cIndex, closestOneCluster.count()))
            sumAndCountOneCluster = closestOneCluster.reduce(lambda p1, p2: (p1[0] + p2[0], p1[1] + p2[1]))

            vectorSum = sumAndCountOneCluster[0]
            count = sumAndCountOneCluster[1]
            newCentroids[cIndex] = vectorSum / count

        tempDist = distanceCentroidsMoved(centroids, newCentroids)
        print("*tempDist=%f\n*centroids=%s\n*newCentroids=%s" % (tempDist, str(centroids), str(newCentroids)))
        centroids = newCentroids[:]  # creates a copy
    print("\n=== Final centers: " + str(centroids))
    print("\ntest partition:")
    bcvVal = bcv(centroids)
    wcvVal = wcv(closest, centroids)
    sseVal = sse(closest, centroids)

    print("SSE: ", end='')
    print(sseVal)
    print("BCV/WCV: ", end='')
    print(bcvVal / wcvVal)

    metrics = [sseVal, bcvVal/wcvVal]
    return metrics

if __name__ == "__main__":
    print(sys.argv) # tested with 100 3 0.015

    if len(sys.argv) != 4:
        # print >> sys.stderr, "Usage: kmeans <file> <k> <convergeDist>"
        print >> sys.stderr, "Usage: kmeans <Npoints> <k> <convergeDist>"
        exit(-1)

    sc = SparkContext(appName="PythonKMeans")
    #    lines = sc.textFile(sys.argv[1])
    #    data = lines.map(parseVector).cache()

    convergeDist = float(sys.argv[3])
    dataLocal = np.load('dataset-problemset2-ex3.npy', mmap_mode='r')
    data = sc.parallelize(dataLocal)

    print("Number of points: %d" % (data.count()))

    # Visualization of the Clusters
    #plt.ion()
    #plt.figure(figsize=(8, 6))

    xValues = []
    sseValues = []
    bwcvValues = []
    for i in range(1, 21):
        evaluate = kmeans(i, data, convergeDist)
        xValues.append(i)
        sseValues.append(evaluate[0])
        bwcvValues.append(evaluate[1])


plt.figure(1)
plt.plot(xValues, sseValues, 'k', color='orange', label='SSE')
legend = plt.legend(loc='upper right', shadow=True)

frame = legend.get_frame()
frame.set_facecolor('0.90')

for label in legend.get_texts():
    label.set_fontsize('large')

for label in legend.get_lines():
    label.set_linewidth(1.5)


plt.figure(2)
plt.plot(xValues, bwcvValues, 'k', color='blue', label='BCV/WCV')
legend = plt.legend(loc='upper left', shadow=True)

frame = legend.get_frame()
frame.set_facecolor('0.90')

for label in legend.get_texts():
    label.set_fontsize('large')

for label in legend.get_lines():
    label.set_linewidth(1.5)


plt.show()

plt.pause(60)

sc.stop()
