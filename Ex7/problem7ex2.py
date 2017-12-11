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

