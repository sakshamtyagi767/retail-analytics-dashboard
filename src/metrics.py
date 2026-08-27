

from typing import Optional, Dict, Any
import numpy as np
import pandas as pd


def calculate_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "total_customers": 0,
            "avg_order_value": 0.0,
            "avg_review_score": 0.0,
            "on_time_delivery_rate": 0.0
        }

    total_revenue = float(df["price"].sum())
    total_orders = int(df["order_id"].nunique())
    total_customers = int(df["customer_unique_id"].nunique())
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
    avg_review = float(df["review_score"].dropna().mean()) if "review_score" in df.columns else 0.0

    # On-time delivery rate among delivered orders
    delivered_df = df[df["order_status"] == "delivered"]
    if not delivered_df.empty and "is_delayed" in delivered_df.columns:
        on_time_rate = float((1 - delivered_df["is_delayed"].mean()) * 100)
    else:
        on_time_rate = 0.0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "avg_order_value": round(avg_order_value, 2),
        "avg_review_score": round(avg_review, 2),
        "on_time_delivery_rate": round(on_time_rate, 1)
    }


def get_monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates revenue and order volume by month.

    Args:
        df (pd.DataFrame): Analytical dataset.

    Returns:
        pd.DataFrame: Monthly trend table with revenue, order count, and AOV.
    """
    if df.empty or "order_year_month" not in df.columns:
        return pd.DataFrame(columns=["order_year_month", "revenue", "order_count", "avg_order_value"])

    trend = df.groupby("order_year_month").agg(
        revenue=("price", "sum"),
        order_count=("order_id", "nunique")
    ).reset_index()

    trend = trend.sort_values("order_year_month")
    trend["avg_order_value"] = trend["revenue"] / trend["order_count"]
    return trend


def get_top_categories(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Computes top product categories by sales revenue and average rating.

    Args:
        df (pd.DataFrame): Analytical dataset.
        top_n (int): Number of top categories to return.

    Returns:
        pd.DataFrame: Category summary table sorted by revenue descending.
    """
    if df.empty or "product_category_name_english" not in df.columns:
        return pd.DataFrame(columns=["category", "revenue", "items_sold", "avg_review_score"])

    cat_df = df.groupby("product_category_name_english").agg(
        revenue=("price", "sum"),
        items_sold=("order_item_id", "count"),
        avg_review_score=("review_score", "mean")
    ).reset_index()

    cat_df.rename(columns={"product_category_name_english": "category"}, inplace=True)
    cat_df = cat_df.sort_values("revenue", ascending=False).head(top_n)
    cat_df["revenue"] = cat_df["revenue"].round(2)
    cat_df["avg_review_score"] = cat_df["avg_review_score"].round(2)
    return cat_df


def calculate_rfm_segments(
    df: pd.DataFrame, 
    snapshot_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Performs RFM (Recency, Frequency, Monetary) analysis and assigns customer personas.

    Args:
        df (pd.DataFrame): Analytical dataset.
        snapshot_date (Optional[pd.Timestamp]): Reference date for recency calculation.

    Returns:
        pd.DataFrame: Customer-level RFM table with Recency, Frequency, Monetary values and Segments.
    """
    if df.empty:
        return pd.DataFrame(columns=["customer_unique_id", "Recency", "Frequency", "Monetary", "Segment"])

    if snapshot_date is None:
        snapshot_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    # Group by customer
    rfm = df.groupby("customer_unique_id").agg(
        Recency=("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
        Frequency=("order_id", "nunique"),
        Monetary=("price", "sum")
    ).reset_index()

    # R Score: lower recency = better score (5 is best)
    rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop")

    # F Score & M Score: higher frequency/monetary = better score (5 is best)
    # Using rank to avoid duplicate bin errors for sparse frequency values
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])

    # Convert scores to integer
    rfm["R_Score"] = rfm["R_Score"].astype(int)
    rfm["F_Score"] = rfm["F_Score"].astype(int)
    rfm["M_Score"] = rfm["M_Score"].astype(int)

    # Segment mapping rules
    def assign_segment(row: pd.Series) -> str:
        r, f = row["R_Score"], row["F_Score"]
        if r >= 4 and f >= 4:
            return "Champions"
        elif f >= 3 and r >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "New / Recent Customers"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2:
            return "Lost Customers"
        else:
            return "Promising / Potential"

    rfm["Segment"] = rfm.apply(assign_segment, axis=1)
    return rfm


def get_delivery_performance_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates delivery SLA metrics grouped by Brazilian state.

    Args:
        df (pd.DataFrame): Analytical dataset.

    Returns:
        pd.DataFrame: Table with state, avg delivery days, and delay rate.
    """
    if df.empty or "customer_state" not in df.columns:
        return pd.DataFrame(columns=["customer_state", "total_orders", "avg_delivery_days", "delayed_rate"])

    delivered = df[df["order_status"] == "delivered"].copy()
    state_perf = delivered.groupby("customer_state").agg(
        total_orders=("order_id", "nunique"),
        avg_delivery_days=("delivery_days", "mean"),
        delayed_rate=("is_delayed", lambda x: (x.mean() * 100))
    ).reset_index()

    state_perf["avg_delivery_days"] = state_perf["avg_delivery_days"].round(1)
    state_perf["delayed_rate"] = state_perf["delayed_rate"].round(1)
    state_perf = state_perf.sort_values("total_orders", ascending=False)
    return state_perf


def get_payment_type_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates breakdown of orders and revenue across payment methods.

    Args:
        df (pd.DataFrame): Analytical dataset.

    Returns:
        pd.DataFrame: Table showing payment method metrics.
    """
    if df.empty or "payment_type" not in df.columns:
        return pd.DataFrame(columns=["payment_type", "order_count", "total_value", "percentage"])

    pay_df = df.groupby("payment_type").agg(
        order_count=("order_id", "nunique"),
        total_value=("total_payment_value", "sum")
    ).reset_index()

    total_val = pay_df["total_value"].sum()
    pay_df["percentage"] = (pay_df["total_value"] / total_val * 100).round(1) if total_val > 0 else 0.0
    pay_df = pay_df.sort_values("total_value", ascending=False)
    return pay_df
