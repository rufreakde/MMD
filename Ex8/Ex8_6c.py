from pyspark.sql import *
from pyspark import *
from pyspark.sql.types import *
from pyspark.sql.functions import *
import sys
import os
from os import listdir
import shutil


def returnDataFrame(pathToFileFolder, spark):
    # Read all files and create an RDD for each file
    DatasetPath = pathToFileFolder + ".txt.gz"
    Schema = StructType([
        StructField("Type", StringType(), True),
        StructField("Price", FloatType(), True),  # alternatively: DecimalType(8, 7)
        StructField("Timestamp", TimestampType(), True),  # alternatively: DateType()
        StructField("InstanceType", StringType(), True),
        StructField("ProductDescription", StringType(), True),
        StructField("AvailabilityZone", StringType(), True)])

    dataFrame = spark.read.csv(DatasetPath, sep='\t', header=True, schema=Schema,
                               timestampFormat="yyyy-MM-dd'T'HH:mm:ss")
    returnDF = dataFrame.drop("Type")

    return returnDF;


def checkDataFrame(df):
    dict = {}
    relevantTable = df.select(df['InstanceType'], df['ProductDescription'], df['AvailabilityZone']).distinct()
    rows = relevantTable.collect()  # a dataset just have about 100-200 distinct lines. thats why we can collect here
    for row in rows:
        temp = df.select(df.Timestamp, df.Price).where(
            (df.InstanceType == row["InstanceType"]) & (df.ProductDescription == row["ProductDescription"]) & (
            df.AvailabilityZone == row["AvailabilityZone"]))
        dict[row["InstanceType"] + ", " + row["ProductDescription"] + ", " + row["AvailabilityZone"]] = temp
    return dict

def saveTimeseries(name, D):
    print("save " + name)
    '''
    Saves a price-time series to disk. If there is a dataframe saved with the same name, load
    this dataframe and merge the two together. Then save the merged one
    :param name: the filename (should pass restriction of a))
    :param D: the price-timeseries to save
    :return: void
    '''
    name_splits = name.split(",")
    if len(name_splits) != 3:
        return "filename didn't pass restriction"

    join = "_".join(name_splits)
    dir_name = "./timeseries/" + join.replace("/", "").replace(" ", "_").replace(".", "")  # replace unwanted chars

    if os.path.isdir(dir_name):
        load_df = spark.read.csv(dir_name, header=True, schema=D.schema)
        df = D.union(load_df)
        df.distinct().write.csv("./timeseries/temp", header=True, mode="overwrite")
        # I had to remove the old directory. I think because spark have problems with my filesystem?
        # error is in the pdf file
        shutil.rmtree(dir_name)
        os.rename("./timeseries/temp", dir_name)
    else:
        D.distinct().write.csv(dir_name, header=True)

if __name__ == '__main__':
    data_files = []
    for file in os.listdir("./EC2-prices"):
        if file.endswith(".txt.gz"):
            data_files.append("./EC2-prices/" + file)

    spark = SparkSession \
        .builder \
        .appName("u8-ex6c-DataFrames") \
        .getOrCreate()

    sc = spark.sparkContext

    for file in data_files:
        foundDF = returnDataFrame(file, spark)
        dict = checkDataFrame(foundDF)
        saveTimeseries("m4.16xlarge, Linux/UNIX, ca-central-1a", dict["m4.16xlarge, Linux/UNIX, ca-central-1a"])

    sc.stop()
