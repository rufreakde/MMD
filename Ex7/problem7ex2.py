<<<<<<< HEAD
from pyspark.sql import *
import re
import sys
import numpy as np
import random

def create_hashfunctions(n):
    a_list = random.sample(range(100),n)
    b_list = random.sample(range(100),n)
    return list(zip(a_list, b_list))


def change_representation(set):
    new_set = [0]*n
    for element in set:
        new_set[element] = 1    
    return new_set


def get_signature(signatures, set, hashfunctions, hash_fnc_index, p, n):
    for j in range(len(hashfunctions)):
        for i in range(len(set)):
            if set[i] == 1:
                hashval = ((hashfunctions[j][0]*i + hashfunctions[j][1]) % p) % n + 1
                if hashval < signatures[i][j]:
                    signatures[i][j] = hashval


if __name__ == '__main__':
    #if len(sys.argv) != 3:
    #    print("Usage: problem6ex2 needs arguments: -k <value>")
    #    print("Argumentlist: " + sys.argv)
    #    exit(-1)

    #k = sys.argv[1]
    #n = sys.argv[2]

    spark = SparkSession \
        .builder \
        .appName("problem7ex2") \
        .getOrCreate()

    sc = spark.sparkContext
    
    nr_of_sets = 1 # adapt for later use
    n = 7 # later given as sys argument
    k = 2 # later given as sys argument
    
    sets = sc.parallelize([1,3,5]) # test set
    sets = sets.map(change_representation) # here we need to change the representation of the sets to the one from the lecture
    print(sets.take(2))
    
    p = 2**31 # define p for the hashfunctions
    hashfunctions = create_hashfunctions(3) # each hasfunction is represented as tuple (a,b)

    signatures = np.full((nr_of_sets, k), 3000000) # initialize signature matrix
    
    
    
    
=======
from pyspark import SparkContext
import numpy as np
import random
from pyspark.sql import *

spark = SparkSession \
    .builder \
    .appName("u7 ex2") \
    .getOrCreate()

sc = spark.sparkContext
sc.addPyFile("problem7ex2.py")

def compute_hash(random_values, n, x):
    p = 2 ** 31 - 1
    hash =  (((random_values[0] * x + random_values[1]) % p) % n) + 1
    return hash

def create_signature(list, hashes):
    permutation = []
    for hash in hashes:  # list of random number a (0) and b (1)
        temp = []
        for x in list:
            temp.append(compute_hash(hash, len(list), x))
        min_value = min(temp)
        permutation.append(min_value)
    return permutation

if __name__ == '__main__':
    k = 4
    p = 2 ** 31 - 1
    list = [[432, 543 ,32, 134, 765], [99, 765, 234, 43, 65], [123, 423, 654, 234, 56]]
    rdd1 = sc.parallelize(list)

    hashes = []
    for i in range(0, k):
        hashes.append(random.sample(range(1, 1000), 2))
    print(hashes)
    max_values = rdd1.map(lambda list: max(list))
    max = max_values.max()

    b = sc.broadcast(hashes)
    rdd2 = rdd1.map(lambda list: create_signature(list, b.value))
    print(rdd2.collect())

>>>>>>> b542141efc05f742c9ba4af19463a10bc1183e8d
