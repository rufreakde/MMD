
import os
import pyspark.sql.functions as func
from pyspark.sql.window import Window
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, TimestampType, StringType, FloatType, StructField


df1 = StructType([
    StructField("Type", StringType(), True),
    StructField("Price", FloatType(), True),
    StructField("Timestamp", TimestampType(), True),
    StructField("InstanceType", StringType(), True),
    StructField("ProductDescription", StringType(), True),
    StructField("AvailabilityZone", StringType(), True)
])
df2 = StructType([
    StructField("Price", FloatType(), True),
    StructField("Timestamp", TimestampType(), True)
])

df3 = StructType([
    StructField("price", FloatType(), True),
    StructField("timestamp-gap-start", TimestampType(), True)
])

def checkCoherency(spark, name=None, df=None):
    if not df:
        name = name.replace('/', '-')
        filename = './timeseries/' + name
        df = spark.read.csv(filename, header=True, schema=df2)
        df = df.groupBy("Timestamp").agg({"Price": "count"}).filter("count(Price) > 1")
        #if len(df.collect()) > 0:
            #print(len(df.collect()))
    return


def checkCompleteness(spark, name, time=(24*60)):
    name = name.replace('/', '-')
    filename = './timeseries/' + name
    df = spark.read.csv(filename, header=True, schema=df3)

    window = Window().partitionBy(func.lit(0)).orderBy(func.col("timestamp-gap-start"))
    df = df.select("*", func.lag("timestamp-gap-start").over(window).alias("timestamp-gap-end")).drop('price')
    df = df.filter(df["timestamp-gap-end"].isNotNull() & ((df["timestamp-gap-start"].cast("bigint") - df["timestamp-gap-end"].cast("bigint"))/60 > time))
    df = df.withColumn("price-series-name", func.lit(name))
    df = df.select(["price-series-name", "timestamp-gap-start", "timestamp-gap-end"])
    #if len(df.collect()) > 0:
        #df.show()
    return df


def readTables(spark, path):
    df = spark.read \
        .csv(path, sep="\t", header=True, schema=df1, timestampFormat="yyyy-MM-dd'T'HH:mm:ss") \
        .drop('Type')
    return df


def generateTimeseries(df):
    unique_map = df.select('InstanceType', 'ProductDescription', 'AvailabilityZone').distinct() \
        .withColumn('name', func.concat_ws('___', 'InstanceType', 'ProductDescription', 'AvailabilityZone')).collect()
    unique_df = {
        item['name']: df.select('Price', 'Timestamp').filter(
            (df.InstanceType == item.InstanceType) & (df.ProductDescription == item.ProductDescription) & (
                    df.AvailabilityZone == item.AvailabilityZone))
        for item in unique_map
    }

    return unique_df


def saveTimeseries(name, D, spark):
    name = name.replace('/', '-')
    filename = './timeseries/' + name

    if os.path.isdir(filename):
        existing = spark.read.csv(filename, header=True, schema=D.schema)
        D = D.union(existing)

    D.distinct().write.csv(filename, header=True, mode='overwrite')


if __name__ == '__main__':
    spark = SparkSession \
        .builder \
        .appName("ex10_6") \
        .getOrCreate()

    initialGeneration = False

    if initialGeneration is True:
        # create ts
        df: DataFrame = readTables(spark, "./EC2-prices/prices-ca-central*.txt.gz")  # used the test files
        time_series = generateTimeseries(df)
        for key, frame in time_series.items():
            saveTimeseries(key, frame, spark)

    dir = os.listdir("./timeseries")
    for file in dir:
        # a)
        checkCoherency(spark, file)
        # b)
        checkCompleteness(spark, file)
