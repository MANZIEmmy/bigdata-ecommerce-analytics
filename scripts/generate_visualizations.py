import os

import matplotlib.pyplot as plt
import pandas as pd


INPUT_DIR = "outputs/final_csv"
OUTPUT_DIR = "outputs/visualizations"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_chart(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# 1. Top 10 products by quantity sold
top_products = pd.read_csv(f"{INPUT_DIR}/top_products.csv").head(10)

plt.figure(figsize=(12, 6))
plt.bar(top_products["product_name"], top_products["total_quantity_sold"])
plt.title("Top 10 Products by Quantity Sold")
plt.xlabel("Product")
plt.ylabel("Total Quantity Sold")
plt.xticks(rotation=75, ha="right")
save_chart("top_products_by_quantity.png")


# 2. Revenue by category
category_revenue = pd.read_csv(f"{INPUT_DIR}/category_revenue.csv")

plt.figure(figsize=(12, 6))
plt.bar(category_revenue["category_name"], category_revenue["total_revenue"])
plt.title("Revenue by Product Category")
plt.xlabel("Category")
plt.ylabel("Total Revenue")
plt.xticks(rotation=75, ha="right")
save_chart("category_revenue.png")


# 3. Monthly revenue trend
monthly_revenue = pd.read_csv(f"{INPUT_DIR}/monthly_revenue_sql.csv")

plt.figure(figsize=(10, 5))
plt.plot(
    monthly_revenue["revenue_month"],
    monthly_revenue["total_revenue"],
    marker="o"
)
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Total Revenue")
plt.grid(True)
save_chart("monthly_revenue_trend.png")


# 4. User segmentation
user_segments = pd.read_csv(f"{INPUT_DIR}/user_segments.csv")
segment_counts = user_segments["segment"].value_counts()

plt.figure(figsize=(8, 5))
plt.bar(segment_counts.index, segment_counts.values)
plt.title("User Segmentation Distribution")
plt.xlabel("User Segment")
plt.ylabel("Number of Users")
save_chart("user_segmentation_distribution.png")


print("All visualizations generated successfully.")