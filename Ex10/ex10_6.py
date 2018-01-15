
import os
import pyspark.sql.functions as func
from pyspark.sql.window import Window
from pyspark.sql import SparkSession
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

def checkCoherency(spark, name=None, dataFrame=None):
    if not dataFrame:
        name = name.replace('/', '-')
        filename = './timeseries/' + name
        dataFrame = spark.read.csv(filename, header=True, schema=df2)
        dataFrame = dataFrame.groupBy("Timestamp").agg({"Price": "count"}).filter("count(Price) > 1")
        if len(dataFrame.collect()) > 0:
            print("Coherency ", len(dataFrame.collect()))
    return


def checkCompleteness(spark, filteredName, time=(24 * 60)):
    filteredName = filteredName.replace('/', '-')
    filepath = './timeseries/' + filteredName
    dataFrame = spark.read.csv(filepath, header=True, schema=df3)

    windowModifier = Window().partitionBy(func.lit(0)).orderBy(func.col("timestamp-gap-start"))
    dataFrame = dataFrame.select("*", func.lag("timestamp-gap-start").over(windowModifier).alias("timestamp-gap-end")).drop('price')
    dataFrame = dataFrame.filter(dataFrame["timestamp-gap-end"].isNotNull() & ((dataFrame["timestamp-gap-start"].cast("bigint") - dataFrame["timestamp-gap-end"].cast("bigint"))/60 >= time))
    dataFrame = dataFrame.withColumn("price-series-name", func.lit(filteredName))
    dataFrame = dataFrame.select(["price-series-name", "timestamp-gap-start", "timestamp-gap-end"])
    if len(dataFrame.collect()) > 0:
        print("Completeness ", len(dataFrame.collect()))
    return dataFrame


def readTables(spark, path):
    dataFrame = spark.read \
        .csv(path, sep="\t", header=True, schema=df1, timestampFormat="yyyy-MM-dd'T'HH:mm:ss") \
        .drop('Type')
    return dataFrame


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


def saveTimeseries(name, dataFrame, spark):
    name = name.replace('/', '-')
    filename = './timeseries/' + name

    if os.path.isdir(filename):
        existing = spark.read.csv(filename, header=True, schema=dataFrame.schema)
        dataFrame = dataFrame.union(existing)

    dataFrame.distinct().write.csv(filename, header=True, mode='overwrite')


if __name__ == '__main__':
    spark = SparkSession \
        .builder \
        .appName("ex10_6") \
        .getOrCreate()

    initialGeneration = False

    if initialGeneration is True:
        # create ts
        dataFrame = readTables(spark, "./EC2-prices/prices-ca-central*.txt.gz")  # used the test files
        time_series = generateTimeseries(dataFrame)
        for key, frame in time_series.items():
            saveTimeseries(key, frame, spark)

    dir = os.listdir("./timeseries")
    for file in dir:
        # a)
        checkCoherency(spark, file)
        # b)
        checkCompleteness(spark, file)
