from pyspark import SparkContext
from scipy.spatial import distance
import numpy as np
import random
import time

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



def merge(_inCluster):
    global sc

    # 1. Compute pairwise distances between all centroids in inCluster
    _distances = sc.parallelize([])
    _inClusterCountN = _inCluster.count()
    keys = _inCluster.keys().collect();

    for cIndex in keys:
        iq, q, pc = _inCluster.filter(lambda element: element[0] == cIndex).collect()[0]
        partialDistances = _inCluster.map(lambda element: (distance.euclidean((element[1][0]/element[2], element[1][1]/element[2]), (q[0]/pc, q[1]/pc)), (element[0], iq), (element[1], q), (pc + element[2])))
        partialDistances = partialDistances.filter(lambda element: element[0] > 0)
        _distances = _distances.union(partialDistances)

    # 2. Find a pair (p,q) of centroids with the smallest distance
    # bestPair = distances.sortBy ( lambda x: x[0] ).first()
    _bestPair = _distances.reduce(getMin) #output is a triple
    #print("____bestPair::")
    #print(_bestPair)

    # 3. Compute centroid r of cluster
    d, (ip, iq), (p, q), pc = _bestPair
    #print(pc)
    _sum = p[0] + q[0]
    _count = p[1] + q[1]
    _r = np.array([_sum, _count]) #this is not right but we have no point count numbers stored?

    _inCluster = _inCluster.filter(lambda element: (element[0] != ip) and (element[0] != iq))
    #print("____inCluster::")
    #print(_inCluster.collect())

    # Psudo code implement here
    #_inClusterCountN = _inCluster.count()
    #for cIndex in range(_inClusterCountN):
    _outCluster = _inCluster.union(sc.parallelize([(startClusterCountN + 1, _r, pc)]))
        #_outCluster = _inCluster.map(lambda x: (cIndex, x))

    #print("____outCluster::")
    #print(_outCluster.collect())

    return _outCluster, _bestPair


def getMin(left, right):
    # left and right are each ( D(p,q), (p,q), (ip,iq) )
    d0, pair0, indices0, pointcount0 = left
    d1, pair1, indices1, pointcount1 = right
    result = left if d0 <= d1 else right
    return result

N = 1
sc = SparkContext(appName='merge')
startTime = time.time()
stopTime = startTime + 300

while time.time() < stopTime:

    #reset time
    startTime = time.time()
    stopTime = startTime + 300

    numpyDataset = []
    numpyDataset = generateData(N, 5) #[[1, 1], [3, 3], [7, 7], [10, 10]];

    #numpyDataset = np.load("dataset-problemset3-ex1-2.npy")
    #print(numpyDataset)

    numpyDatasetRearanged = []
    for idx,Dataset in enumerate(numpyDataset):
        numpyDatasetRearanged.append((idx, Dataset, 1)) #third parameter is pointcount

    inCluster = sc.parallelize(numpyDatasetRearanged)  # = RDD with pairs(point_index, point
    startClusterCountN = inCluster.count()
    merged = []

    while inCluster.count() > 1:
        #print("inCluster::")
        #print(inCluster.collect())
        outCluster, outMerged = merge(inCluster)
        startClusterCountN += 1
        merged.append(outMerged)
        inCluster = outCluster

    timeTaken = time.time() - startTime
    #print(inCluster.collect())
    print("Time: " + str(timeTaken) + " N: " + str(N));
    N += 1

#print("inCluster::")
#print(inCluster.collect())
#print("Merged::")
#print(merged)
