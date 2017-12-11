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
    
    
    
    