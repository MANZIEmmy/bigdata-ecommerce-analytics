# Project Execution Log

## Project Title

Distributed Multi-Model Analytics for E-commerce Data

## Objective

The objective of this project is to build a distributed analytics pipeline for synthetic e-commerce data using MongoDB, HBase, and Apache Spark. The system stores different types of data in suitable storage models, performs analytics using Spark, and produces outputs and visualizations for reporting.

---

## 1. Development Environment

The project was implemented on Windows 10 using Docker containers and Python scripts.

### Host Environment

| Tool             | Version / Status                |
| ---------------- | ------------------------------- |
| Operating System | Windows 10                      |
| Docker           | Docker version 29.5.3           |
| Docker Compose   | Docker Compose v5.1.4           |
| Java             | OpenJDK 17.0.19 Temurin         |
| Python           | Python 3.13.1                   |
| VS Code          | 1.111.0                         |
| Git Bash         | Used for command-line execution |

### Docker Services

The project used Docker Compose to run the required distributed system components.

| Service      | Docker Image         | Purpose                              |
| ------------ | -------------------- | ------------------------------------ |
| MongoDB      | `mongo:7`            | Document database                    |
| Apache Spark | `apache/spark:3.5.3` | Spark master and analytics execution |
| Spark Worker | `apache/spark:3.5.3` | Spark worker node                    |
| HBase        | `dajobe/hbase`       | Distributed wide-column storage      |

---

## 2. Project Structure

The project folder was organized as follows:

```text
AUCA-BIGDATA-PROJECT/
├── data/
├── docs/
├── outputs/
├── reports/
├── screenshots/
├── scripts/
├── README.md
├── dataset_generator.ipynb
├── docker-compose.yml
├── requirements.txt
└── .gitignore
```

### Important Folders

| Folder         | Purpose                                         |
| -------------- | ----------------------------------------------- |
| `data/`        | Stores generated JSON datasets                  |
| `scripts/`     | Stores Python and Spark scripts                 |
| `outputs/`     | Stores Spark outputs and visualizations         |
| `docs/`        | Stores technical documentation                  |
| `reports/`     | Stores project log and final report materials   |
| `screenshots/` | Stores evidence screenshots for final reporting |

---

## 3. Dataset Generation

The project used the provided dataset generator notebook:

```text
dataset_generator.ipynb
```

The generated datasets were saved in the `data/` folder.

### Generated Files

```text
data/users.json
data/categories.json
data/products.json
data/transactions.json
data/sessions_0.json
```

### Development Dataset Configuration

A reduced dataset was used during development to allow faster testing and debugging.

| Entity       | Development Count |
| ------------ | ----------------: |
| Users        |               100 |
| Products     |               100 |
| Categories   |                10 |
| Transactions |              1000 |
| Sessions     |              5000 |
| Timespan     |           90 days |

### Original Full Dataset Configuration

The original generator supports a larger final-scale configuration.

| Entity       | Original Count |
| ------------ | -------------: |
| Users        |          10000 |
| Products     |           5000 |
| Categories   |             25 |
| Transactions |         500000 |
| Sessions     |        2000000 |
| Timespan     |        90 days |

### Development Note

The reduced dataset was used only for development and validation. The same pipeline can be executed on the larger dataset configuration, although full-scale execution requires more processing time and system resources.

---

## 4. MongoDB Implementation

MongoDB was used to store document-oriented e-commerce data.

### Database Name

```text
ecommerce
```

### Collections

```text
users
categories
products
transactions
sessions
```

### Import Method

The generated JSON files were JSON arrays, so the `--jsonArray` option was used with `mongoimport`.

Example:

```bash
docker exec -i mongodb mongoimport \
  --db ecommerce \
  --collection users \
  --jsonArray \
  < data/users.json
```

### Imported Document Counts

| Collection   | Documents Imported |
| ------------ | -----------------: |
| users        |                100 |
| categories   |                 10 |
| products     |                100 |
| transactions |               1000 |
| sessions     |               5000 |

### MongoDB Analytics Completed

The following MongoDB aggregations were implemented:

| Aggregation         | Purpose                                                  |
| ------------------- | -------------------------------------------------------- |
| Product popularity  | Identified top-selling products by quantity              |
| Revenue by category | Calculated total revenue and quantity sold per category  |
| User segmentation   | Classified users by transaction count and total spending |

### MongoDB Indexes Created

```javascript
db.transactions.createIndex({ user_id: 1 })
db.transactions.createIndex({ "items.product_id": 1 })
db.products.createIndex({ product_id: 1 })
db.products.createIndex({ category_id: 1 })
db.categories.createIndex({ category_id: 1 })
db.sessions.createIndex({ user_id: 1 })
```

### Index Purpose

| Index                           | Purpose                               |
| ------------------------------- | ------------------------------------- |
| `transactions.user_id`          | Speeds up user transaction analysis   |
| `transactions.items.product_id` | Supports product popularity queries   |
| `products.product_id`           | Supports joins with transaction items |
| `products.category_id`          | Supports category analytics           |
| `categories.category_id`        | Supports category lookup              |
| `sessions.user_id`              | Supports session lookup by user       |

---

## 5. HBase Implementation

HBase was used to store e-commerce session data.

### Table Name

```text
user_sessions
```

### Column Families

```text
info
device
activity
cart
```

### Row Key Design

```text
user_id#start_time#session_id
```

Example:

```text
user_000068#2026-04-05T02:38:08#sess_fd011b4e68
```

### Row Key Justification

| Component    | Purpose                                               |
| ------------ | ----------------------------------------------------- |
| `user_id`    | Enables retrieval of all sessions for a specific user |
| `start_time` | Preserves chronological session ordering              |
| `session_id` | Ensures uniqueness                                    |

### Table Creation

```ruby
create 'user_sessions', 'info', 'device', 'activity', 'cart'
```

### Loading Method

A Python script was created to load session records into HBase:

```text
scripts/load_sessions_to_hbase.py
```

During development, the script loaded the first 100 sessions from:

```text
data/sessions_0.json
```

### HBase Verification

The row count was verified using:

```ruby
count 'user_sessions'
```

Result:

```text
101 row(s)
```

This included:

| Source              | Rows |
| ------------------- | ---: |
| Manual test row     |    1 |
| Loaded session rows |  100 |
| Total               |  101 |

### User Session Query

A prefix scan was used to retrieve sessions for a specific user:

```ruby
scan 'user_sessions', {
  FILTER => "PrefixFilter('user_000068')"
}
```

Result:

```text
3 row(s)
```

### HBase Result

The HBase implementation successfully demonstrated table creation, session loading, row count verification, and user-specific session retrieval.

---

## 6. Apache Spark Implementation

Apache Spark was used for batch analytics and Spark SQL processing.

### Spark Environment

| Component                   | Version              |
| --------------------------- | -------------------- |
| Spark                       | 3.5.3                |
| Scala                       | 2.12.18              |
| Java inside Spark container | 11.0.24              |
| Docker image                | `apache/spark:3.5.3` |

### Project Folder Mounting

The project folder was mounted into the Spark container through Docker Compose:

```yaml
volumes:
  - .:/opt/spark/work-dir
working_dir: /opt/spark/work-dir
```

This allowed Spark to access project files such as:

```text
data/
scripts/
outputs/
reports/
```

### Spark Path Note

Because Git Bash converts Linux-style paths, Spark commands were executed using double slash syntax:

```bash
docker exec spark //opt/spark/bin/spark-submit scripts/spark_check.py
```

---

## 7. Spark Validation

A validation script was created:

```text
scripts/spark_check.py
```

The script confirmed Spark could read all JSON files using multiline JSON mode:

```python
spark.read.option("multiLine", "true").json(path)
```

### Spark Dataset Counts

| Dataset      | Rows |
| ------------ | ---: |
| users        |  100 |
| products     |  100 |
| categories   |   10 |
| transactions | 1000 |
| sessions     | 5000 |

This confirmed that Spark could access and read all project datasets.

---

## 8. Spark Analytics

The main Spark analytics script was created:

```text
scripts/spark_analytics.py
```

### Processing Steps

The script performed:

1. Data loading
2. Timestamp conversion
3. Date extraction
4. User registration month extraction
5. Transaction item normalization using `explode`
6. Product popularity analysis
7. Category revenue analysis
8. User segmentation
9. Product affinity analysis
10. Cohort analysis
11. Spark SQL monthly revenue analysis
12. CSV output generation

### Analytics Produced

| Output                    | Description                                         |
| ------------------------- | --------------------------------------------------- |
| `top_products.csv`        | Top products by quantity sold                       |
| `category_revenue.csv`    | Revenue by product category                         |
| `user_segments.csv`       | User-level spending and segmentation                |
| `product_affinity.csv`    | Product pairs bought together                       |
| `cohort_analysis.csv`     | User activity by registration and transaction month |
| `monthly_revenue_sql.csv` | Monthly revenue using Spark SQL                     |

### Clean Output Folder

Spark initially produced partitioned CSV output folders. Clean CSV copies were then created in:

```text
outputs/final_csv/
```

Final CSV files:

```text
outputs/final_csv/category_revenue.csv
outputs/final_csv/cohort_analysis.csv
outputs/final_csv/monthly_revenue_sql.csv
outputs/final_csv/product_affinity.csv
outputs/final_csv/top_products.csv
outputs/final_csv/user_segments.csv
```

### Spark Execution Result

The Spark analytics script completed successfully and saved output files into the `outputs/` folder.

---

## 9. Visualizations

A visualization script was created:

```text
scripts/generate_visualizations.py
```

The script used Pandas and Matplotlib to create static visualizations from Spark output CSV files.

### Generated Visualizations

```text
outputs/visualizations/top_products_by_quantity.png
outputs/visualizations/category_revenue.png
outputs/visualizations/monthly_revenue_trend.png
outputs/visualizations/user_segmentation_distribution.png
```

### Visualization Purpose

| Visualization                  | Purpose                                    |
| ------------------------------ | ------------------------------------------ |
| Top products by quantity sold  | Shows most popular products                |
| Revenue by category            | Compares revenue across product categories |
| Monthly revenue trend          | Shows revenue movement over time           |
| User segmentation distribution | Shows the number of users in each segment  |

The visualization phase was completed successfully.

---

## 10. Documentation Files Created

The following documentation files were created:

```text
docs/mongodb.md
docs/hbase.md
docs/spark.md
reports/project_log.md
README.md
requirements.txt
.gitignore
```

### Documentation Purpose

| File                     | Purpose                                      |
| ------------------------ | -------------------------------------------- |
| `README.md`              | General project overview                     |
| `docs/mongodb.md`        | MongoDB implementation details               |
| `docs/hbase.md`          | HBase schema and loading explanation         |
| `docs/spark.md`          | Spark analytics explanation                  |
| `reports/project_log.md` | Complete project execution record            |
| `requirements.txt`       | Python package requirements                  |
| `.gitignore`             | Files and folders excluded from Git tracking |

---

## 11. Completed Requirements

| Project Requirement             | Status    |
| ------------------------------- | --------- |
| Dataset generation              | Completed |
| MongoDB schema and loading      | Completed |
| MongoDB aggregations            | Completed |
| MongoDB indexes                 | Completed |
| HBase table design              | Completed |
| HBase session loading           | Completed |
| HBase user session query        | Completed |
| Spark batch processing          | Completed |
| Data cleaning and normalization | Completed |
| Spark SQL analytics             | Completed |
| Product affinity analysis       | Completed |
| Cohort analysis                 | Completed |
| Static visualizations           | Completed |
| Project structure setup         | Completed |
| Technical documentation         | Completed |

---

## 12. Pending Work

The following tasks remain before final submission:

1. Capture screenshots for evidence.
2. Prepare the final 6–8 page PDF report.
3. Add selected screenshots and visualizations to the final report.
4. Review all scripts and documentation.
5. Push the complete project to GitHub.
6. Submit the GitHub repository link and final PDF report.

---

## 13. Summary

The project successfully implemented a distributed multi-model analytics pipeline for synthetic e-commerce data. MongoDB was used for document storage and aggregation, HBase was used for session data storage and row-key-based retrieval, and Apache Spark was used for batch analytics, Spark SQL, and output generation. The final outputs include cleaned CSV analytics and static visualizations suitable for inclusion in the final report.
