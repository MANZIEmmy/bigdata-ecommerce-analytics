# Apache Spark Implementation

## Purpose

Apache Spark was used for distributed batch analytics on the generated e-commerce datasets. Spark is suitable for this project because it can process large datasets, perform transformations on nested data, run SQL queries, and generate analytical outputs for reporting and visualization.

## Spark Environment

Spark was executed inside a Docker container.

```text
Spark version: 3.5.3
Scala version: 2.12.18
Java version inside container: 11.0.24
Docker image: apache/spark:3.5.3
```

## Project Folder Mounting

The project folder was mounted into the Spark container using Docker Compose.

```yaml
volumes:
  - .:/opt/spark/work-dir
working_dir: /opt/spark/work-dir
```

This allowed Spark to access:

```text
data/
scripts/
outputs/
reports/
```

## Spark Validation Script

Before running analytics, Spark access to the dataset was validated using:

```text
scripts/spark_check.py
```

The validation script read all JSON files using multiline JSON mode because the generated files were JSON arrays.

```python
spark.read.option("multiLine", "true").json(path)
```

## Dataset Counts Verified in Spark

| Dataset      | Rows |
| ------------ | ---: |
| users        |  100 |
| products     |  100 |
| categories   |   10 |
| transactions | 1000 |
| sessions     | 5000 |

This confirmed that Spark could successfully read all generated datasets.

## Main Analytics Script

The main Spark analytics script was:

```text
scripts/spark_analytics.py
```

This script performed data loading, cleaning, normalization, analytical transformations, Spark SQL queries, and output generation.

## Data Cleaning and Normalization

The transactions dataset was cleaned by converting timestamp fields into Spark timestamp and date columns.

```python
transactions_clean = transactions \
    .withColumn("transaction_ts", to_timestamp(col("timestamp"))) \
    .withColumn("transaction_date", to_date(col("transaction_ts")))
```

The users dataset was cleaned by extracting registration month.

```python
users_clean = users \
    .withColumn("registration_ts", to_timestamp(col("registration_date"))) \
    .withColumn("registration_month", date_format(col("registration_ts"), "yyyy-MM"))
```

Transaction items were normalized by exploding the nested `items` array.

```python
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
    )
```

This transformed nested transaction records into product-level line items.

## Analytics Produced

### 1. Product Popularity

Calculated the most purchased products by total quantity sold.

Output:

```text
outputs/final_csv/top_products.csv
```

### 2. Revenue by Category

Joined transaction line items with product and category data to calculate revenue by product category.

Output:

```text
outputs/final_csv/category_revenue.csv
```

### 3. User Segmentation

Grouped users by transaction count and total spending.

Segments used:

```text
High Value: more than 15 transactions
Medium Value: 5 to 15 transactions
Low Value: fewer than 5 transactions
```

Output:

```text
outputs/final_csv/user_segments.csv
```

### 4. Product Affinity Analysis

Generated pairs of products bought together in the same transaction.

Output:

```text
outputs/final_csv/product_affinity.csv
```

The highest product pairs were sorted by:

```text
times_bought_together
```

### 5. Cohort Analysis

Grouped customers by registration month and transaction month to analyze user activity and revenue over time.

Output:

```text
outputs/final_csv/cohort_analysis.csv
```

### 6. Monthly Revenue Using Spark SQL

A temporary SQL view was created from cleaned transactions.

```python
transactions_clean.createOrReplaceTempView("transactions")
```

Spark SQL was then used to calculate monthly revenue.

```sql
SELECT
    date_format(transaction_ts, 'yyyy-MM') AS revenue_month,
    COUNT(DISTINCT transaction_id) AS transaction_count,
    ROUND(SUM(total), 2) AS total_revenue,
    ROUND(AVG(total), 2) AS average_transaction_value
FROM transactions
GROUP BY date_format(transaction_ts, 'yyyy-MM')
ORDER BY revenue_month
```

Output:

```text
outputs/final_csv/monthly_revenue_sql.csv
```

## Final Spark Output Files

Clean CSV output files were stored in:

```text
outputs/final_csv/
```

Files generated:

```text
category_revenue.csv
cohort_analysis.csv
monthly_revenue_sql.csv
product_affinity.csv
top_products.csv
user_segments.csv
```

## Visualization Inputs

The Spark output CSV files were used as input for the visualization script:

```text
scripts/generate_visualizations.py
```

The generated visualizations were saved in:

```text
outputs/visualizations/
```

## Summary

Apache Spark was successfully used to process and analyze the generated e-commerce data. The implementation included data cleaning, nested data normalization, product popularity analysis, category revenue analysis, user segmentation, product affinity analysis, cohort analysis, and Spark SQL monthly revenue analysis.
