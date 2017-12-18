
from pyspark.sql import *
from pyspark import *
from pyspark.sql.types import *
from pyspark.sql.functions import *
import sys
import os
from os import listdir
import shutil

def returnDataFrame(pathToFileFolder, spark):
    #Read all files and create an RDD for each file
    DatasetPath = pathToFileFolder + ".txt.gz"
    Schema = StructType([
        StructField("Type", StringType(), True),
        StructField("Price", FloatType(), True), #alternatively: DecimalType(8, 7)
        StructField("Timestamp", TimestampType(), True), #alternatively: DateType()
        StructField("InstanceType", StringType(), True),
        StructField("ProductDescription", StringType(), True),
        StructField("AvailabilityZone", StringType(), True)])

    dataFrame = spark.read.csv(DatasetPath, sep='\t', header=True, schema=Schema, timestampFormat="yyyy-MM-dd'T'HH:mm:ss")
    returnDF = dataFrame.drop("Type")

    return returnDF;

def checkDataFrame(df):
    dict = {}
    relevantTable = df.select(df['InstanceType'], df['ProductDescription'], df['AvailabilityZone']).distinct().limit(2)
    rows = relevantTable.collect()  # a dataset just have about 100-200 distinct lines. thats why we can collect here
    for row in rows:
        temp = df.select(df.Timestamp, df.Price).where((df.InstanceType == row["InstanceType"]) & (df.ProductDescription == row["ProductDescription"]) & (df.AvailabilityZone == row["AvailabilityZone"]))
        dict[row["InstanceType"] + ", " + row["ProductDescription"] + ", " + row["AvailabilityZone"]] = temp
    return dict
    #dict['c4.2xlarge Linux/UNIX ap-northeast-2c'].show()  # test output

def saveTimeseries(name, D):
    '''
    Saves a price-time series to disk. If there is a dataframe saved with the same name, load
    this dataframe and merge the two together. Then save the merged one
    :param name: the filename (should pass restriction of a))
    :param D: the price-timeseries to save
    :return: void
    '''
    D.printSchema()
    name_splits = name.split(",")
    if len(name_splits) != 3:
        return "filename didn't pass restriction"

    join = "_".join(name_splits)
    filename = join.replace("/", "_").replace(" ", "_")
    print(filename)

    datafile = ""
    if os.path.isdir(filename):
        filenames = listdir(filename)
        for file in filenames:
            if file.endswith(".csv"):
                datafile = file
    print(datafile)
    if datafile != "":
        print("existiert")
        #  load dataframe and merge the two
        Schema = StructType([
            StructField("Timestamp", TimestampType(), True),
            StructField("Price", FloatType(), True)])

        load_df = spark.read.csv(filename + "/" + datafile, header=True, schema=Schema, timestampFormat="yyyy-MM-dd'T'HH:mm:ss")
        merged = D.union(load_df).distinct()
        merged.show(3)
        print(merged.count())
        merged.printSchema()
        merged.write.csv("./temp", mode="overwrite", header=True)
        shutil.rmtree(filename)
        os.rename("./temp", "./"+filename)
    else:
        # save dataframe to disk
        D.write.csv("./"+filename, mode="overwrite", header=True)

if __name__ == '__main__':
    data_files = []
	for file in os.listdir("./amazon_data"):
		if file.endswith(".csv"):
			data_files.append(file)
    

    spark = SparkSession \
        .builder \
        .appName("u8-ex6b-DataFrames") \
        .getOrCreate()

    sc = spark.sparkContext
	
	for file in data_files:
		foundDF = returnDataFrame(pathToFileFolder, spark)
		dict = checkDataFrame(foundDF)
		saveTimeseries("m4.16xlarge, Linux/UNIX, ca-central-1a", dict["m4.16xlarge, Linux/UNIX, ca-central-1a"])

    sc.stop()