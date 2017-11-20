from pyspark import SparkContext
from scipy.spatial import distance
import numpy as np
from pyspark.sql import *
from pyspark.sql.types import *

def PearsonCorrelationCoefficient( df, user1, user2):

    #mean1 = df.filter(df["User"] == user1).rdd.reduce(lambda row1, row2: (row1[2] + row2[2]))
    mean1DF = df.filter(df["User"] == user1)
    count1 = mean1DF.count()
    sum1 = mean1DF.rdd.map(lambda row: row[2]).sum()
    user1ArtistMap = mean1DF.rdd.map(lambda row: (row[1], (row[0], row[2])))
    mean1 = sum1 / count1
    #print(mean1)
    mean2DF = df.filter(df["User"] == user2)
    count2 = mean2DF.count()
    sum2 = mean2DF.rdd.map(lambda row: row[2]).sum()
    user2ArtistMap = mean2DF.rdd.map(lambda row: (row[1], (row[0], row[2])))
    mean2 = sum2 / count2
    #print(mean2)
    unionRDD = user1ArtistMap.union(user2ArtistMap).reduceByKey(lambda x, y: [x, y]).filter(lambda elem: isinstance(elem[1], list))
    #value1 = unionRDD.map(lambda elem: (elem[1][1][0][1] - mean1)*((elem[1][1][1][1] - mean2))).sum()
    value1 = unionRDD.map(lambda elem: (elem[1][0][1] - mean1)*(elem[1][1][1] - mean2))
    nominator = value1.sum()

    value2 = unionRDD.map(lambda elem: ((elem[1][0][1] - mean1)**2)).sum()**0.5
    value3 = unionRDD.map(lambda elem: ((elem[1][1][1] - mean2) ** 2)).sum()**0.5

    denominator = value2 * value3

    pearson = nominator / denominator
    #print(pearson)
    return pearson



spark = SparkSession \
    .builder \
    .appName("ps4 ex5") \
    .getOrCreate()

sc = spark.sparkContext
if __name__ == '__main__':

    #Read the dataset

#artist_alias_small.
    ArtistAliasSmall = sc.textFile('./dataset-problemset4-ex5/AAS.txt').map(lambda line: line.split())
    ArtistAliasSmallRDD = ArtistAliasSmall.map(lambda p: (p[0], p[1].strip()))
    ArtistAliasCollectedMap = ArtistAliasSmallRDD.collectAsMap()

#user_artist_data_small
    UserArtistDataSmall = sc.textFile('./dataset-problemset4-ex5/UADS.txt').map(lambda line:line.split())
    UserArtistDataSmallRDD = UserArtistDataSmall.map(lambda p: (int(p[0]), int(p[1]), int(p[2].strip())))
    UserArtistDataSmallRDD = UserArtistDataSmallRDD.map(lambda element:
                                                                element if element[1] not in ArtistAliasCollectedMap
                                                                else
                                                                    (element[0], ArtistAliasCollectedMap[element[1]], element[2])
                                                        )

    #artist_data_small
    ArtistDataSmall = sc.textFile('./dataset-problemset4-ex5/ADS.txt').map(lambda line: line.split(maxsplit=1))
    ArtistDataSmallRDD = ArtistDataSmall.map(lambda p: (p[0], p[1].strip()))


    UtilityMatrix = UserArtistDataSmallRDD.toDF(['User', 'Artist', 'Data'])
    #print("UtilityMatrix:")
    #UtilityMatrix.show()

    PearsonCorrelationCoefficient(UtilityMatrix, 101, 102)


