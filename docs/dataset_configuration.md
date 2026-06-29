# Dataset Configuration

## Purpose

This document records the dataset configuration used in the project. The project originally provides a large-scale dataset configuration, but a smaller development configuration was used during local implementation and testing.

This distinction is important because the project must remain faithful to the provided requirements while also being practical to execute on a local Windows 10 Docker environment.

---

## Original Provided Configuration

The original dataset generator configuration supports large-scale e-commerce data generation.

```python
NUM_USERS = 10000
NUM_PRODUCTS = 5000
NUM_CATEGORIES = 25
NUM_TRANSACTIONS = 500000
NUM_SESSIONS = 2000000
TIMESPAN_DAYS = 90
```

This configuration represents the intended full-scale dataset for the project.

---

## Development Configuration Used

For local development, testing, debugging, and validation, the dataset size was reduced.

```python
NUM_USERS = 100
NUM_PRODUCTS = 100
NUM_CATEGORIES = 10
NUM_TRANSACTIONS = 1000
NUM_SESSIONS = 5000
TIMESPAN_DAYS = 90
```

This reduced configuration allowed the pipeline to be developed and tested efficiently on a local Windows 10 machine using Docker containers.

---

## Generated Development Files

The reduced configuration generated the following files:

```text
data/users.json
data/categories.json
data/products.json
data/transactions.json
data/sessions_0.json
```

---

## Reason for Using the Development Configuration

The original dataset is large and would require more time, memory, storage, and processing resources. Since the goal during development was to validate system design, database loading, query logic, Spark processing, and visualization generation, a smaller dataset was used first.

The reduced dataset was used to confirm that:

* MongoDB could load and aggregate the generated data.
* HBase could store and query session data.
* Spark could read, clean, normalize, and analyze the datasets.
* CSV outputs and visualizations could be generated successfully.
* The complete project pipeline worked from data generation to reporting outputs.

---

## Important Final Report Note

The final report should clearly state that the project pipeline was developed and validated using a reduced dataset for local testing, while the original configuration remains the full-scale target configuration.

Recommended wording:

> The original dataset generator supports a large-scale configuration of 10,000 users, 5,000 products, 25 categories, 500,000 transactions, and 2,000,000 sessions over 90 days. During local development and testing, a reduced configuration was used to allow faster execution on a Windows 10 Docker environment. The reduced dataset was used to validate the full pipeline design, including MongoDB loading and aggregation, HBase session storage, Spark analytics, Spark SQL, and visualization generation. The same implementation design can be executed on the original larger configuration with sufficient computing resources.

---

## Summary

Both configurations are documented to preserve transparency. The reduced dataset was used only for development and validation. The project design, storage models, analytics logic, and reporting outputs remain aligned with the original project requirements.
