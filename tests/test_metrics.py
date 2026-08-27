"""
Unit Tests for Business Analytics Metrics.

Tests KPI calculation, monthly sales trend aggregation, top product categories,
RFM customer segmentation, and delivery SLA calculations using Pytest.
"""

import pandas as pd
import pytest
from src.metrics import (
    calculate_executive_kpis,
    get_monthly_sales_trend,
    get_top_categories,
    calculate_rfm_segments,
    get_delivery_performance_by_state,
    get_payment_type_distribution,
)


@pytest.fixture
def sample_analytical_df() -> pd.DataFrame:
    """
    Creates a synthetic DataFrame mocking the joined analytical dataset.
    """
    data = {
        "order_id": ["o1", "o2", "o3", "o4"],
        "customer_id": ["c1", "c2", "c3", "c4"],
        "customer_unique_id": ["u1", "u2", "u1", "u3"],
        "price": [100.0, 200.0, 150.0, 50.0],
        "freight_value": [10.0, 20.0, 15.0, 5.0],
        "total_payment_value": [110.0, 220.0, 165.0, 55.0],
        "payment_type": ["credit_card", "boleto", "credit_card", "voucher"],
        "review_score": [5.0, 4.0, 5.0, 2.0],
        "order_status": ["delivered", "delivered", "delivered", "delivered"],
        "is_delayed": [0, 1, 0, 0],
        "delivery_days": [5, 12, 4, 3],
        "customer_state": ["SP", "RJ", "SP", "MG"],
        "product_category_name_english": ["Health Beauty", "Bed Bath Table", "Health Beauty", "Watches Gifts"],
        "order_item_id": [1, 1, 1, 1],
        "order_purchase_timestamp": pd.to_datetime([
            "2023-01-10", "2023-01-15", "2023-02-10", "2023-02-20"
        ]),
        "order_year_month": ["2023-01", "2023-01", "2023-02", "2023-02"]
    }
    return pd.DataFrame(data)


def test_calculate_executive_kpis(sample_analytical_df: pd.DataFrame) -> None:
    """
    Tests calculation of top-line KPIs (Revenue, Orders, AOV, Review Score).
    """
    kpis = calculate_executive_kpis(sample_analytical_df)

    assert kpis["total_revenue"] == 500.0
    assert kpis["total_orders"] == 4
    assert kpis["total_customers"] == 3
    assert kpis["avg_order_value"] == 125.0
    assert kpis["avg_review_score"] == 4.0
    # 3 on time out of 4 delivered = 75.0%
    assert kpis["on_time_delivery_rate"] == 75.0


def test_calculate_executive_kpis_empty() -> None:
    """
    Tests KPI calculation behavior when input DataFrame is empty.
    """
    empty_df = pd.DataFrame()
    kpis = calculate_executive_kpis(empty_df)
    assert kpis["total_revenue"] == 0.0
    assert kpis["total_orders"] == 0
    assert kpis["on_time_delivery_rate"] == 0.0


def test_get_monthly_sales_trend(sample_analytical_df: pd.DataFrame) -> None:
    """
    Tests monthly aggregation of revenue and order counts.
    """
    trend = get_monthly_sales_trend(sample_analytical_df)

    assert len(trend) == 2
    assert list(trend["order_year_month"]) == ["2023-01", "2023-02"]
    # Jan revenue: 100 + 200 = 300
    jan_row = trend[trend["order_year_month"] == "2023-01"].iloc[0]
    assert jan_row["revenue"] == 300.0
    assert jan_row["order_count"] == 2


def test_get_top_categories(sample_analytical_df: pd.DataFrame) -> None:
    """
    Tests top category ranking by revenue.
    """
    cats = get_top_categories(sample_analytical_df, top_n=2)

    assert len(cats) == 2
    top_cat = cats.iloc[0]
    # Health Beauty total revenue: 100 + 150 = 250
    assert top_cat["category"] == "Health Beauty"
    assert top_cat["revenue"] == 250.0


def test_calculate_rfm_segments(sample_analytical_df: pd.DataFrame) -> None:
    """
    Tests customer RFM segmentation scoring and output columns.
    """
    rfm = calculate_rfm_segments(sample_analytical_df)

    assert not rfm.empty
    assert "customer_unique_id" in rfm.columns
    assert "Segment" in rfm.columns
    assert set(rfm["customer_unique_id"]) == {"u1", "u2", "u3"}


def test_get_delivery_performance_by_state(sample_analytical_df: pd.DataFrame) -> None:
    """
    Tests state-level delivery performance metrics.
    """
    perf = get_delivery_performance_by_state(sample_analytical_df)

    assert "customer_state" in perf.columns
    sp_row = perf[perf["customer_state"] == "SP"].iloc[0]
    assert sp_row["total_orders"] == 2
    assert sp_row["delayed_rate"] == 0.0
