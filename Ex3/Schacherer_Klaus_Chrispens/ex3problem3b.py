from pyspark import SparkContext

if __name__ == "__main__":
    sc = SparkContext(appName="PythonKMeans")

    lines = sc.textFile("lorem_ipsum.txt")
    lineLengths = lines.map(lambda s: len(s))
    totalLength = lineLengths.reduce(lambda a, b: a + b)

    print(totalLength)

    sc.stop()