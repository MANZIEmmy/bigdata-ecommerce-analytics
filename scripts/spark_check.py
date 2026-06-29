from pyspark.sql import SparkSession


spark = SparkSession.builder \
    .appName("AUCA E-commerce Spark Data Check") \
    .getOrCreate()


files = {
    "users": "data/users.json",
    "products": "data/products.json",
    "categories": "data/categories.json",
    "transactions": "data/transactions.json",
    "sessions": "data/sessions_0.json"
}


for name, path in files.items():
    df = spark.read.option("multiLine", "true").json(path)
    print(f"{name}: {df.count()} rows")
    df.printSchema()


spark.stop()