from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    count,
    countDistinct,
    date_format,
    desc,
    explode,
    round,
    sum as spark_sum,
    to_date,
    to_timestamp,
    when,
)


spark = SparkSession.builder \
    .appName("AUCA E-commerce Spark Analytics") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


def read_json(path):
    return spark.read.option("multiLine", "true").json(path)


def write_csv(df, output_path):
    df.coalesce(1) \
        .write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(output_path)


# 1. Load datasets
users = read_json("data/users.json")
products = read_json("data/products.json")
categories = read_json("data/categories.json")
transactions = read_json("data/transactions.json")
sessions = read_json("data/sessions_0.json")


# 2. Clean and normalize data
transactions_clean = transactions \
    .withColumn("transaction_ts", to_timestamp(col("timestamp"))) \
    .withColumn("transaction_date", to_date(col("transaction_ts")))

users_clean = users \
    .withColumn("registration_ts", to_timestamp(col("registration_date"))) \
    .withColumn("registration_month", date_format(col("registration_ts"), "yyyy-MM"))

product_dim = products.select(
    "product_id",
    col("name").alias("product_name"),
    "category_id",
    "base_price",
    "current_stock",
    "is_active"
)

category_dim = categories.select(
    "category_id",
    col("name").alias("category_name")
)


# 3. Normalize transaction items
line_items = transactions_clean \
    .select(
        "transaction_id",
        "user_id",
        "session_id",
        "payment_method",
        "status",
        "transaction_ts",
        "transaction_date",
        explode(col("items")).alias("item")
    ) \
    .select(
        "transaction_id",
        "user_id",
        "session_id",
        "payment_method",
        "status",
        "transaction_ts",
        "transaction_date",
        col("item.product_id").alias("product_id"),
        col("item.quantity").alias("quantity"),
        col("item.unit_price").alias("unit_price"),
        col("item.subtotal").alias("item_subtotal")
    )


# 4. Product popularity analysis
top_products = line_items \
    .groupBy("product_id") \
    .agg(
        spark_sum("quantity").alias("total_quantity_sold"),
        round(spark_sum("item_subtotal"), 2).alias("total_item_revenue"),
        countDistinct("transaction_id").alias("transaction_count")
    ) \
    .join(product_dim, "product_id", "left") \
    .select(
        "product_id",
        "product_name",
        "category_id",
        "total_quantity_sold",
        "total_item_revenue",
        "transaction_count"
    ) \
    .orderBy(desc("total_quantity_sold"))


# 5. Revenue by category
category_revenue = line_items \
    .join(product_dim, "product_id", "left") \
    .join(category_dim, "category_id", "left") \
    .groupBy("category_id", "category_name") \
    .agg(
        round(spark_sum("item_subtotal"), 2).alias("total_revenue"),
        spark_sum("quantity").alias("total_quantity_sold"),
        countDistinct("transaction_id").alias("transaction_count")
    ) \
    .orderBy(desc("total_revenue"))


# 6. User segmentation
user_segments = transactions_clean \
    .groupBy("user_id") \
    .agg(
        countDistinct("transaction_id").alias("transaction_count"),
        round(spark_sum("total"), 2).alias("total_spent"),
        round(avg("total"), 2).alias("average_order_value")
    ) \
    .withColumn(
        "segment",
        when(col("transaction_count") > 15, "High Value")
        .when(col("transaction_count") >= 5, "Medium Value")
        .otherwise("Low Value")
    ) \
    .orderBy(desc("total_spent"))


# 7. Product affinity analysis
transaction_products = line_items \
    .select("transaction_id", "product_id") \
    .distinct()

product_pairs = transaction_products.alias("a") \
    .join(transaction_products.alias("b"), "transaction_id") \
    .where(col("a.product_id") < col("b.product_id")) \
    .groupBy(
        col("a.product_id").alias("product_a"),
        col("b.product_id").alias("product_b")
    ) \
    .agg(count("*").alias("times_bought_together")) \
    .orderBy(desc("times_bought_together"))

product_a_dim = product_dim.select(
    col("product_id").alias("product_a"),
    col("product_name").alias("product_a_name")
)

product_b_dim = product_dim.select(
    col("product_id").alias("product_b"),
    col("product_name").alias("product_b_name")
)

product_affinity = product_pairs \
    .join(product_a_dim, "product_a", "left") \
    .join(product_b_dim, "product_b", "left") \
    .select(
        "product_a",
        "product_a_name",
        "product_b",
        "product_b_name",
        "times_bought_together"
    ) \
    .orderBy(desc("times_bought_together"))


# 8. Cohort analysis
cohort_analysis = transactions_clean \
    .join(users_clean.select("user_id", "registration_month"), "user_id", "left") \
    .withColumn("transaction_month", date_format(col("transaction_ts"), "yyyy-MM")) \
    .groupBy("registration_month", "transaction_month") \
    .agg(
        countDistinct("user_id").alias("active_users"),
        countDistinct("transaction_id").alias("transaction_count"),
        round(spark_sum("total"), 2).alias("revenue")
    ) \
    .orderBy("registration_month", "transaction_month")


# 9. Spark SQL analytics
transactions_clean.createOrReplaceTempView("transactions")

monthly_revenue_sql = spark.sql("""
    SELECT
        date_format(transaction_ts, 'yyyy-MM') AS revenue_month,
        COUNT(DISTINCT transaction_id) AS transaction_count,
        ROUND(SUM(total), 2) AS total_revenue,
        ROUND(AVG(total), 2) AS average_transaction_value
    FROM transactions
    GROUP BY date_format(transaction_ts, 'yyyy-MM')
    ORDER BY revenue_month
""")


# 10. Write outputs
write_csv(top_products, "outputs/top_products")
write_csv(category_revenue, "outputs/category_revenue")
write_csv(user_segments, "outputs/user_segments")
write_csv(product_affinity, "outputs/product_affinity")
write_csv(cohort_analysis, "outputs/cohort_analysis")
write_csv(monthly_revenue_sql, "outputs/monthly_revenue_sql")


# 11. Display key results
print("\n=== TOP PRODUCTS ===")
top_products.show(10, truncate=False)

print("\n=== CATEGORY REVENUE ===")
category_revenue.show(10, truncate=False)

print("\n=== USER SEGMENTS ===")
user_segments.show(10, truncate=False)

print("\n=== PRODUCT AFFINITY ===")
product_affinity.show(10, truncate=False)

print("\n=== COHORT ANALYSIS ===")
cohort_analysis.show(10, truncate=False)

print("\n=== MONTHLY REVENUE SQL ===")
monthly_revenue_sql.show(10, truncate=False)

print("\nSpark analytics completed successfully.")
print("Output files saved in the outputs/ folder.")

spark.stop()