
import os
os.environ["PYSPARK_PYTHON"]="/usr/local/bin/python3"

from pyspark.sql import SparkSession


if __name__ == "__main__":

    spark = SparkSession\
        .builder\
        .appName("U1 - Exercise 2")\
        .getOrCreate()

    #sparkcontext
    sc = spark.sparkContext

#TRANSFORMS
    #intersection()
    intersectRDD1 = sc.parallelize(range(1, 10))
    intersectRDD2 = sc.parallelize(range(5, 15))
    intersect = intersectRDD1.intersection(intersectRDD2).collect()
    print(intersect)
    #[8, 9, 5, 6, 7]

    #distinct()
    distinctRDD1 = sc.parallelize(range(1, 12))
    distinctRDD2 = sc.parallelize(range(8, 20))
    distinct = distinctRDD1.union(distinctRDD2).distinct().collect()
    print(distinct)
    #[8, 16, 1, 9, 17, 2, 10, 18, 3, 11, 19, 4, 12, 5, 13, 6, 14, 7, 15]

    #union()
    unionRDD1 = sc.parallelize(range(1, 7))
    unionRDD2 = sc.parallelize(range(3, 10))
    union = unionRDD1.union(unionRDD2).collect()
    print(union)
    #[1, 2, 3, 4, 5, 6, 3, 4, 5, 6, 7, 8, 9]

#ACTIONS
    #collect()
    collection = sc.parallelize([1, 2, 3, 4, 5]).flatMap(lambda x: [x, x, x]).collect()
    print(collection)
    #[1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]

    #count()
    names1RDD = sc.parallelize(["Daniela", "Marvin", "Rudolf", "Kevin", "Jaqueline"])
    counts = names1RDD.count()
    print(counts)
    #5

    #first()
    names2RDD = sc.parallelize(["Daniela", "Marvin", "Rudolf"])
    first = names2RDD.first()
    print(first)
    #Daniela

    spark.stop()
