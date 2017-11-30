from pyspark import SparkContext
import numpy as np
from pyspark.sql import *
from pyspark.sql.types import *

spark = SparkSession \
    .builder \
    .appName("u6 ex2") \
    .getOrCreate()

sc = spark.sparkContext
sc.addPyFile("problem6ex2.py")

def filter_hyphen(element):
    if element[len(element)-1] is "-":
        return element[0:len(element)-1]
    else:
        return element

def shingle(element, k):
    return element

if __name__ == '__main__':
    k = 5

    strings = ["hjgzuds", "ihuihiiu -", "kj-hkjhkjh -"]
    rdd = sc.parallelize(strings)\
        .map(lambda e: filter_hyphen(e))\
        .flatMap(lambda e: e)\
        .map(lambda e: shingle(e, k))
    #rdd2 = rdd.flatMap(lambda e: e).filter(lambda e: e is not "h")

    print(rdd)


    #files = ["pg44016.txt"]

    #for filename in files:
    #    temp_rdd = sc.textFile("./textfiles/" + filename)
    #    col = temp_rdd.take(10)
    #    print(col)

sc.stop()