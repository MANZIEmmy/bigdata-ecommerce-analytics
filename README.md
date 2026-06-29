# Distributed Multi-Model Analytics for E-commerce Data

This project implements a distributed analytics pipeline for synthetic e-commerce data using MongoDB, HBase, and Apache Spark.

## Technologies Used

* MongoDB for document-based storage and aggregation
* HBase for distributed session storage
* Apache Spark for batch analytics and Spark SQL
* Python for data generation, loading, analytics, and visualization
* Docker Compose for container orchestration

## Project Structure

```text
data/                  Generated JSON datasets
scripts/               Python and Spark scripts
outputs/               Spark analytics outputs and visualizations
docs/                  Technical documentation
reports/               Project logs and final report materials
screenshots/           Evidence screenshots for report
docker-compose.yml     Docker services for MongoDB, Spark, and HBase
requirements.txt       Python package requirements
```

## Main Scripts

* `scripts/load_sessions_to_hbase.py` loads session data into HBase.
* `scripts/spark_check.py` validates Spark access to JSON datasets.
* `scripts/spark_analytics.py` performs Spark batch analytics.
* `scripts/generate_visualizations.py` creates static visualizations.

## Generated Outputs

* Top products
* Category revenue
* User segmentation
* Product affinity
* Cohort analysis
* Monthly revenue using Spark SQL

## Development Note

During development, a reduced dataset was used for faster testing. The original project configuration supports a much larger dataset for final-scale execution.
