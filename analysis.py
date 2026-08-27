

import os
import sys
from src.data_loader import load_and_clean_data
from src.metrics import (
    calculate_executive_kpis,
    get_monthly_sales_trend,
    get_top_categories,
    calculate_rfm_segments,
    get_delivery_performance_by_state,
)


def run_analysis() -> None:
    
    print("=" * 60)
    print("   RETAIL ANALYTICS DASHBOARD - EXECUTIVE CLI SUMMARY REPORT")
    print("=" * 60)
    print("\n[1/4] Loading and cleaning Olist datasets...")
    
    try:
        df = load_and_clean_data(data_dir="data/archive")
        print(f"-> Successfully loaded {len(df):,} total order items.")
    except Exception as e:
        print(f"Error loading datasets: {e}")
        sys.exit(1)

    print("\n[2/4] Calculating Executive KPIs...")
    kpis = calculate_executive_kpis(df)
    
    print("-" * 60)
    print(f"  Total Revenue              : ${kpis['total_revenue']:,.2f}")
    print(f"  Total Orders               : {kpis['total_orders']:,}")
    print(f"  Total Unique Customers     : {kpis['total_customers']:,}")
    print(f"  Average Order Value (AOV)  : ${kpis['avg_order_value']:,.2f}")
    print(f"  Average Review Score       : {kpis['avg_review_score']} / 5.0")
    print(f"  On-Time Delivery Rate      : {kpis['on_time_delivery_rate']}%")
    print("-" * 60)

    print("\n[3/4] Top 5 Product Categories by Revenue:")
    top_cats = get_top_categories(df, top_n=5)
    for idx, row in top_cats.iterrows():
        print(f"  {row['category']:<30} | Revenue: ${row['revenue']:>10,.2f} | Items Sold: {row['items_sold']:>6,}")

    print("\n[4/4] Customer RFM Segmentation Overview:")
    rfm_df = calculate_rfm_segments(df)
    segment_counts = rfm_df["Segment"].value_counts()
    for segment, count in segment_counts.items():
        pct = (count / len(rfm_df)) * 100
        print(f"  {segment:<25} : {count:>6,} customers ({pct:>5.1f}%)")

    print("\n" + "=" * 60)
    print("Analysis execution complete! Launch Streamlit app with: streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    run_analysis()
