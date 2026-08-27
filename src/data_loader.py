

import os
from typing import Optional
import pandas as pd


def load_raw_datasets(data_dir: str) -> dict[str, pd.DataFrame]:
    
    files = {
        "orders": "olist_orders_dataset.csv",
        "items": "olist_order_items_dataset.csv",
        "customers": "olist_customers_dataset.csv",
        "payments": "olist_order_payments_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv",
        "products": "olist_products_dataset.csv",
        "translation": "product_category_name_translation.csv"
    }
    
    datasets: dict[str, pd.DataFrame] = {}
    for key, filename in files.items():
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required dataset file not found: {file_path}")
        datasets[key] = pd.read_csv(file_path)
        
    return datasets


def load_and_clean_data(data_dir: str = "data/archive") -> pd.DataFrame:
    
    raw_data = load_raw_datasets(data_dir)
    
    orders_df = raw_data["orders"]
    items_df = raw_data["items"]
    customers_df = raw_data["customers"]
    payments_df = raw_data["payments"]
    reviews_df = raw_data["reviews"]
    products_df = raw_data["products"]
    translation_df = raw_data["translation"]

    # 1. Parse datetime fields
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_columns:
        if col in orders_df.columns:
            orders_df[col] = pd.to_datetime(orders_df[col], errors="coerce")

    # 2. Translate product category names
    products_translated = pd.merge(
        products_df,
        translation_df,
        on="product_category_name",
        how="left"
    )
    products_translated["product_category_name_english"] = (
        products_translated["product_category_name_english"]
        .fillna("others")
        .str.replace("_", " ")
        .str.title()
    )

    # 3. Aggregate payments by order_id (taking sum of payment value & main payment type)
    payment_agg = payments_df.groupby("order_id").agg(
        total_payment_value=("payment_value", "sum"),
        payment_type=("payment_type", lambda x: x.mode()[0] if not x.empty else "unknown"),
        payment_installments=("payment_installments", "max")
    ).reset_index()

    # 4. Aggregate reviews by order_id (taking mean review score)
    review_agg = reviews_df.groupby("order_id").agg(
        review_score=("review_score", "mean")
    ).reset_index()

    # 5. Merge all relational tables
    df = orders_df.merge(customers_df, on="customer_id", how="inner")
    df = df.merge(items_df, on="order_id", how="inner")
    df = df.merge(products_translated[["product_id", "product_category_name_english"]], on="product_id", how="left")
    df = df.merge(payment_agg, on="order_id", how="left")
    df = df.merge(review_agg, on="order_id", how="left")

    # 6. Derive key analytics metrics & flags
    # Calculate item-level total item price + freight
    df["total_order_item_value"] = df["price"] + df["freight_value"]
    
    # Calculate delivery duration in days
    df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    df["estimated_delivery_days"] = (df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]).dt.days
    
    # Delayed flag (1 if delivered after estimated date, else 0)
    df["is_delayed"] = (df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]).astype(int)
    
    # Temporal metrics
    df["order_year"] = df["order_purchase_timestamp"].dt.year
    df["order_month"] = df["order_purchase_timestamp"].dt.month
    df["order_year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    
    return df
