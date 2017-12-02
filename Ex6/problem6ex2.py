from pyspark.sql import *
import re
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: problem6ex2 needs arguments: -k <value>")
        print("Argumentlist: " + sys.argv)
        exit(-1)

    shingleSize = int(sys.argv[2])

    spark = SparkSession \
        .builder \
        .appName("u6-ex2-GenCharShingles") \
        .getOrCreate()

    sc = spark.sparkContext
    sc.addPyFile("problem6ex2.py")

#Read all files automatic with spark and format them right for thurder use
    #delete - at line end and delete line end afterwards (replace with space)
    documents = sc.wholeTextFiles('./textfiles') \
        .mapValues(lambda txt: re.sub('-(\r)?\n', '', txt))\
        .mapValues(lambda txt: re.sub('(\r)?\n', ' ', txt))\
        .zipWithIndex()

#Tthis is the shingle dataset with K=9 over 10 documents in folder textfiles
    shingled = documents.map(lambda item: (item[1], item[0][1])) \
        .flatMapValues(lambda element: [element[start:start + shingleSize] for start in range(0, len(element))]) \
        .distinct()

#THIS PART IS JUST FOR COMPARE PRINTING!
    outputForCompare = shingled \
        .map(lambda element: (element[0], 1)) \
        .reduceByKey(lambda a, b: a + b) \

    print_key_val_pair = documents.map(lambda item: (item[1], item[0][0].split('/')[-1]))

    new = outputForCompare.join(print_key_val_pair)

    print("k == " + str(shingleSize))
    print("pg44016 == The White Spark, by Orville Livingston Leach")
    print(new.collect())
