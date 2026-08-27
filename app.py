

from typing import Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import load_and_clean_data
from src.metrics import (
    calculate_executive_kpis,
    get_monthly_sales_trend,
    get_top_categories,
    calculate_rfm_segments,
    get_delivery_performance_by_state,
    get_payment_type_distribution,
)

# Set page configuration
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(show_spinner="Loading and cleaning 100k+ order records...")
def get_dataset() -> pd.DataFrame:
    """
    Cached function to load and clean raw datasets.
    """
    return load_and_clean_data(data_dir="data/archive")


def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
   
    st.sidebar.header("🔍 Global Dashboard Filters")

    # Date range filter
    min_date = df["order_purchase_timestamp"].min().date()
    max_date = df["order_purchase_timestamp"].max().date()

    selected_dates = st.sidebar.date_input(
        "Select Purchase Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        df_filtered = df[
            (df["order_purchase_timestamp"].dt.date >= start_date) &
            (df["order_purchase_timestamp"].dt.date <= end_date)
        ]
    else:
        df_filtered = df.copy()

    # State filter
    all_states = sorted(df_filtered["customer_state"].dropna().unique().tolist())
    selected_states = st.sidebar.multiselect(
        "Filter by Customer State",
        options=all_states,
        default=[]
    )
    if selected_states:
        df_filtered = df_filtered[df_filtered["customer_state"].isin(selected_states)]

    # Category filter
    all_categories = sorted(df_filtered["product_category_name_english"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Filter by Product Category",
        options=all_categories,
        default=[]
    )
    if selected_categories:
        df_filtered = df_filtered[df_filtered["product_category_name_english"].isin(selected_categories)]

    st.sidebar.markdown("---")
    st.sidebar.info(f"Showing **{len(df_filtered):,}** of **{len(df):,}** items.")

    return df_filtered


def main() -> None:
    """
    Main application entry point rendering dashboard layout and tabs.
    """
    st.title("🛒 Executive Retail Analytics Dashboard")
    st.caption("Real-Time E-Commerce Performance, RFM Segmentation & Logistics SLA Analytics")

    df_raw = get_dataset()
    df = apply_sidebar_filters(df_raw)

    if df.empty:
        st.warning("No records match the selected filter criteria. Please adjust filters.")
        return

    # Calculate Executive KPIs
    kpis = calculate_executive_kpis(df)

    # Top KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
    col2.metric("Total Orders", f"{kpis['total_orders']:,}")
    col3.metric("Avg Order Value", f"${kpis['avg_order_value']:,.2f}")
    col4.metric("On-Time SLA Rate", f"{kpis['on_time_delivery_rate']}%")
    col5.metric("Avg Rating", f"{kpis['avg_review_score']} / 5.0")

    st.markdown("---")

    # Dashboard Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Sales & Revenue Trends",
        "👥 Customer RFM Segmentation",
        "📦 Product & Category Analysis",
        "🚚 Logistics & Payments",
        "📋 Data Table & Export"
    ])

    # -----------------------------
    # TAB 1: Sales & Revenue Trends
    # -----------------------------
    with tab1:
        st.subheader("Monthly Revenue & Order Volume Growth")
        monthly_df = get_monthly_sales_trend(df)

        if not monthly_df.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=monthly_df["order_year_month"],
                y=monthly_df["revenue"],
                name="Revenue ($)",
                marker_color="#1f77b4"
            ))
            fig_trend.add_trace(go.Scatter(
                x=monthly_df["order_year_month"],
                y=monthly_df["order_count"],
                name="Order Count",
                yaxis="y2",
                mode="lines+markers",
                line=dict(color="#ff7f0e", width=3)
            ))
            fig_trend.update_layout(
                title="Monthly Gross Revenue ($) and Total Orders",
                xaxis=dict(title="Month"),
                yaxis=dict(title="Revenue ($)"),
                yaxis2=dict(title="Order Count", overlaying="y", side="right"),
                legend=dict(x=0.01, y=0.99),
                height=450
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No monthly trend data available.")

    # -----------------------------
    # TAB 2: RFM Customer Segmentation
    # -----------------------------
    with tab2:
        st.subheader("Customer Recency, Frequency & Monetary (RFM) Personas")
        st.write("Customers grouped into behavioural segments based on purchase history.")

        rfm_df = calculate_rfm_segments(df)
        if not rfm_df.empty:
            seg_summary = rfm_df["Segment"].value_counts().reset_index()
            seg_summary.columns = ["Segment", "Customer Count"]

            col_rfm1, col_rfm2 = st.columns([1, 1])

            with col_rfm1:
                fig_rfm_pie = px.pie(
                    seg_summary,
                    names="Segment",
                    values="Customer Count",
                    title="Customer Distribution by Persona Segment",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig_rfm_pie, use_container_width=True)

            with col_rfm2:
                fig_rfm_bar = px.bar(
                    seg_summary,
                    x="Segment",
                    y="Customer Count",
                    color="Segment",
                    title="Customer Volume per Segment",
                    text_auto=True,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig_rfm_bar, use_container_width=True)

            # Informative personas guide
            st.markdown("""
            **Segment Definitions & Recommended Action Plan:**
            - **🏆 Champions**: Highly active, recent, and big spenders. *Strategy: Reward loyalty, early access to new releases.*
            - **💙 Loyal Customers**: Regular buyers with consistent history. *Strategy: Upsell premium products and subscriptions.*
            - **⚡ New / Recent Customers**: Bought recently but low order frequency. *Strategy: Onboarding campaigns & discount coupons.*
            - **⚠️ At Risk**: High historical spenders who haven't ordered recently. *Strategy: Win-back email promotions & customer surveys.*
            - **❌ Lost Customers**: Lowest recency and lowest frequency. *Strategy: Low-cost re-engagement or automated archival.*
            """)

    # -----------------------------
    # TAB 3: Product & Category Analysis
    # -----------------------------
    with tab3:
        st.subheader("Product Category Revenue & Performance Ranking")
        top_cat_df = get_top_categories(df, top_n=15)

        if not top_cat_df.empty:
            fig_cat = px.bar(
                top_cat_df,
                x="revenue",
                y="category",
                orientation="h",
                color="revenue",
                title="Top 15 Product Categories by Revenue ($)",
                labels={"revenue": "Revenue ($)", "category": "Product Category"},
                color_continuous_scale="Viridis"
            )
            fig_cat.update_layout(yaxis=dict(autorange="reversed"), height=500)
            st.plotly_chart(fig_cat, use_container_width=True)

            st.dataframe(top_cat_df, use_container_width=True)

    # -----------------------------
    # TAB 4: Logistics & Payments
    # -----------------------------
    with tab4:
        st.subheader("Logistics Delivery SLA & Payment Breakdown")

        col_log1, col_log2 = st.columns(2)

        with col_log1:
            st.markdown("#### Delivery Performance by Customer State (Top 10)")
            state_df = get_delivery_performance_by_state(df).head(10)
            fig_state = px.bar(
                state_df,
                x="customer_state",
                y="avg_delivery_days",
                color="delayed_rate",
                title="Avg Delivery Days & Delayed Rate (%) by State",
                labels={"avg_delivery_days": "Avg Delivery (Days)", "delayed_rate": "Late Delivery %"},
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_state, use_container_width=True)

        with col_log2:
            st.markdown("#### Payment Method Distribution")
            pay_df = get_payment_type_distribution(df)
            fig_pay = px.pie(
                pay_df,
                names="payment_type",
                values="total_value",
                title="Revenue Share by Payment Method",
                hole=0.3
            )
            st.plotly_chart(fig_pay, use_container_width=True)

    # -----------------------------
    # TAB 5: Data Table & Export
    # -----------------------------
    with tab5:
        st.subheader("Filtered Dataset View")
        display_cols = [
            "order_id", "order_purchase_timestamp", "customer_state",
            "product_category_name_english", "price", "freight_value",
            "payment_type", "order_status", "review_score"
        ]
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available_cols].head(500), use_container_width=True)

        # Export CSV Button
        csv_data = df[available_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Data to CSV",
            data=csv_data,
            file_name="filtered_retail_analytics_data.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
