# MongoDB Implementation

## Purpose

MongoDB was used as the document-oriented database for storing structured and semi-structured e-commerce data. It is suitable for this project because the generated dataset contains nested fields such as product price history, transaction items, and user geographic information.

## Database Name

```text
ecommerce
```

## Collections Used

```text
users
categories
products
transactions
sessions
```

## Imported Dataset Sizes

During development, a reduced dataset was used for faster testing.

| Collection   | Documents Imported |
| ------------ | -----------------: |
| users        |                100 |
| categories   |                 10 |
| products     |                100 |
| transactions |               1000 |
| sessions     |               5000 |

## Import Method

The generated JSON files were stored as JSON arrays. Therefore, the `--jsonArray` option was required during import.

Example import commands:

```bash
docker exec -i mongodb mongoimport \
  --db ecommerce \
  --collection users \
  --jsonArray \
  < data/users.json
```

```bash
docker exec -i mongodb mongoimport \
  --db ecommerce \
  --collection products \
  --jsonArray \
  < data/products.json
```

```bash
docker exec -i mongodb mongoimport \
  --db ecommerce \
  --collection transactions \
  --jsonArray \
  < data/transactions.json
```

## Schema Design

### Users Collection

Stores customer profile information.

Important fields:

```text
user_id
geo_data.city
geo_data.state
geo_data.country
registration_date
last_active
```

### Products Collection

Stores product catalog information.

Important fields:

```text
product_id
name
category_id
base_price
current_stock
is_active
price_history
creation_date
```

### Categories Collection

Stores product category information.

Important fields:

```text
category_id
name
subcategories
```

### Transactions Collection

Stores purchase transactions.

Important fields:

```text
transaction_id
session_id
user_id
timestamp
items
subtotal
discount
total
payment_method
status
```

The `items` field is an embedded array containing product-level purchase details.

### Sessions Collection

Stores browsing session data.

Important fields:

```text
session_id
user_id
start_time
end_time
device_profile
viewed_products
page_views
cart_contents
conversion_status
```

## MongoDB Aggregations

### 1. Product Popularity

This aggregation identifies the most frequently purchased products.

```javascript
db.transactions.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.product_id",
      total_quantity_sold: { $sum: "$items.quantity" }
    }
  },
  { $sort: { total_quantity_sold: -1 } },
  { $limit: 10 }
])
```

### 2. Revenue by Category

This aggregation joins transactions with products and categories to calculate total revenue per category.

```javascript
db.transactions.aggregate([
  { $unwind: "$items" },
  {
    $lookup: {
      from: "products",
      localField: "items.product_id",
      foreignField: "product_id",
      as: "product_info"
    }
  },
  { $unwind: "$product_info" },
  {
    $group: {
      _id: "$product_info.category_id",
      total_revenue: { $sum: "$items.subtotal" },
      total_quantity_sold: { $sum: "$items.quantity" }
    }
  },
  {
    $lookup: {
      from: "categories",
      localField: "_id",
      foreignField: "category_id",
      as: "category_info"
    }
  },
  { $unwind: "$category_info" },
  {
    $project: {
      _id: 0,
      category_id: "$_id",
      category_name: "$category_info.name",
      total_revenue: { $round: ["$total_revenue", 2] },
      total_quantity_sold: 1
    }
  },
  { $sort: { total_revenue: -1 } }
])
```

### 3. User Segmentation

This aggregation groups users according to transaction frequency and total spending.

```javascript
db.transactions.aggregate([
  {
    $group: {
      _id: "$user_id",
      transaction_count: { $sum: 1 },
      total_spent: { $sum: "$total" }
    }
  },
  {
    $project: {
      _id: 0,
      user_id: "$_id",
      transaction_count: 1,
      total_spent: { $round: ["$total_spent", 2] },
      segment: {
        $switch: {
          branches: [
            { case: { $gt: ["$transaction_count", 15] }, then: "High Value" },
            { case: { $gte: ["$transaction_count", 5] }, then: "Medium Value" }
          ],
          default: "Low Value"
        }
      }
    }
  },
  { $sort: { total_spent: -1 } }
])
```

## Indexes Created

The following indexes were created to improve query performance.

```javascript
db.transactions.createIndex({ user_id: 1 })
db.transactions.createIndex({ "items.product_id": 1 })
db.products.createIndex({ product_id: 1 })
db.products.createIndex({ category_id: 1 })
db.categories.createIndex({ category_id: 1 })
db.sessions.createIndex({ user_id: 1 })
```

## Index Justification

| Index                           | Purpose                                          |
| ------------------------------- | ------------------------------------------------ |
| `transactions.user_id`          | Speeds up user-level transaction analysis        |
| `transactions.items.product_id` | Supports product popularity queries              |
| `products.product_id`           | Supports joins between transactions and products |
| `products.category_id`          | Supports category-level analytics                |
| `categories.category_id`        | Supports category lookup joins                   |
| `sessions.user_id`              | Supports retrieval of sessions by user           |

## Summary

MongoDB was used to store the main e-commerce entities and perform document-based aggregations. The implementation successfully loaded users, products, categories, transactions, and sessions. It also produced business analytics such as product popularity, category revenue, and user segmentation.
