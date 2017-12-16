
from pyspark.sql import *
from pyspark import *
from pyspark.sql.types import *
from pyspark.sql.functions import *
import sys

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
    relevantTable = df.select(df['InstanceType'], df['ProductDescription'], df['AvailabilityZone']).distinct()
    rows = relevantTable.collect()  # a dataset just have about 100-200 distinct lines. thats why we can collect here
    for row in rows:
        temp = df.select(df.Timestamp, df.Price).where((df.InstanceType == row["InstanceType"]) & (df.ProductDescription == row["ProductDescription"]) & (df.AvailabilityZone == row["AvailabilityZone"]))
        dict[row["InstanceType"] + " " + row["ProductDescription"] + " " + row["AvailabilityZone"]] = temp
    dict['c4.2xlarge Linux/UNIX ap-northeast-2c'].show()  # test output

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: Ex7_4 needs arguments:\n -f <./Path/To/Folder/FileName>")
        print("Argumentlist: ", sys.argv)
        exit(-1)

    pathToFileFolder = ''
    if(sys.argv[1] == '-f'):
        pathToFileFolder = str(sys.argv[2])
    else:
        print("ERROR: No File specified\nArgumentlist: " + sys.argv)

    spark = SparkSession \
        .builder \
        .appName("u7-ex4-DataFrames") \
        .getOrCreate()

    sc = spark.sparkContext

    foundDF = returnDataFrame(pathToFileFolder, spark)

    checkDataFrame(foundDF)
    sc.stop()