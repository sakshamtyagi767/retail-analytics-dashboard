# 📘 Complete Guide: Building an Executive Retail Analytics Dashboard & Interview Handbook

Welcome to the official master guide for the **Retail Analytics Dashboard** project. This guide was written specifically to help you master every single line of code, understand how real-world data analytics applications are structured, and confidently answer interview questions when applying for Data Analyst roles.

---

## 💡 Section 1: Conceptual Core & Real-World Analogies

Before writing code, let's understand the core software and analytical concepts using simple everyday analogies.

### 1. The Data ETL Pipeline (Extract, Transform, Load)
* **Simple Analogy**: Imagine running a **high-end restaurant kitchen**.
  * **Extract (Raw Data)**: The raw ingredients arriving in crates from various suppliers (farms, fisheries, bakeries). In our project, these are raw, unorganized CSV files (`olist_orders.csv`, `olist_customers.csv`).
  * **Transform (Data Cleaning & Merging)**: The kitchen sous-chefs washing vegetables, chopping meats, and combining raw ingredients together according to a recipe. In code (`src/data_loader.py`), we convert timestamps, translate Portuguese product names to English, and join tables together using primary keys (`order_id`, `customer_id`).
  * **Load (Analytical Dataset)**: The clean, prepped dish placed on the hot line ready for cooking. In code, this is our clean pandas DataFrame ready for analysis.

### 2. Modular Architecture (`src/` vs `app.py`)
* **Simple Analogy**: Think of a **television set**.
  * The **Backend (`src/metrics.py`)** is like the internal electronic circuit boards and processors that calculate the signal.
  * The **Frontend (`app.py`)** is the sleek TV screen that displays the visual image to the user.
  * **Why keep them separate?** If you want to change the TV screen size (or build a mobile app instead of Streamlit), you don't need to rebuild the internal circuit boards.

### 3. Customer RFM Segmentation
* **Simple Analogy**: Think of an **Airline Frequent Flyer Program**.
  * **Recency (R)**: How many days ago did the passenger fly? (Flyers who flew yesterday get higher attention than those who haven't flown in 2 years).
  * **Frequency (F)**: How many total flights has the passenger taken this year?
  * **Monetary (M)**: How much money has the passenger spent on tickets?
  * Passengers with high R, F, and M get **First Class VIP status (Champions)**. Passengers with low R and high F are **Dormant Frequent Flyers (At Risk)** who need special discount emails to come back.

---

## 🔗 Section 2: How All Files Are Connected

Here is a visual map showing how data flows through the project from raw CSV files to interactive charts and unit tests:

```
[Raw CSV Files in data/archive/]
  ├── olist_orders_dataset.csv
  ├── olist_customers_dataset.csv
  ├── olist_order_items_dataset.csv
  ├── olist_order_payments_dataset.csv
  ├── olist_products_dataset.csv
  └── product_category_name_translation.csv
                     │
                     ▼
           [src/data_loader.py] ◄── Loads, cleans dates, translates categories & merges on IDs
                     │
                     ▼
           [Unified Clean DataFrame]
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
 [src/metrics.py]         [tests/test_metrics.py]
 (Calculates KPIs,         (Pytest validates metric logic
  RFM, Trends, SLA)         using synthetic sample data)
         │
    ┌────┴────────────────────────┐
    ▼                             ▼
[analysis.py]                 [app.py]
(CLI Terminal Report)         (Interactive Streamlit Web Dashboard)
```

---

## 🛠️ Section 3: How to Build This Project Step-by-Step

If you were building this project from complete scratch, follow these 5 steps:

1. **Step 1: Set Up Directory & Requirements**
   - Create project folder and virtual environment.
   - Define minimal dependencies in `requirement.txt`: `pandas`, `numpy`, `plotly`, `streamlit`, `pytest`.

2. **Step 2: Build the Data Ingestion Pipeline (`src/data_loader.py`)**
   - Load each raw CSV using Pandas.
   - Convert string date columns into Python `datetime` objects (`pd.to_datetime`).
   - Merge relational tables using inner/left joins on relational keys (`order_id`, `customer_id`, `product_id`).
   - Calculate derived metrics like `delivery_days` and `is_delayed`.

3. **Step 3: Build the Business Logic Engine (`src/metrics.py`)**
   - Write modular, pure Python functions with clear type hints.
   - Calculate Executive KPIs (Revenue, AOV, Orders).
   - Implement RFM quantiles (`pd.qcut`) to categorize customer segments.
   - Group by Brazilian states to calculate delivery delays.

4. **Step 4: Write Unit Tests (`tests/test_metrics.py`)**
   - Use `pytest` fixtures to mock a sample DataFrame.
   - Assert that `calculate_executive_kpis` and `get_monthly_sales_trend` compute mathematically accurate numbers.

5. **Step 5: Build the Interactive Dashboard UI (`app.py`)**
   - Set up Streamlit layout with multi-tab structure.
   - Add sidebar date range, state, and category filters.
   - Render interactive Plotly charts for revenue trends, customer segments, and logistics SLA.

---

## 🔍 Section 4: Detailed Line-by-Line File Explanations

Let's examine every single file and understand what each line does.

---

### File 1: `src/data_loader.py`

```python
1: """
2: Data Loader Module for Retail Analytics Dashboard.
3: ...
4: """
```
* **Lines 1-4**: Module docstring explaining the file's responsibility.

```python
5: import os
6: from typing import Optional
7: import pandas as pd
```
* **Lines 5-7**: Imports standard operating system library `os`, type hinting helper `Optional`, and `pandas` for data manipulation.

```python
10: def load_raw_datasets(data_dir: str) -> dict[str, pd.DataFrame]:
```
* **Line 10**: Defines function `load_raw_datasets` accepting `data_dir` string path and returning a dictionary mapping dataset names to Pandas DataFrames.

```python
19:     files = {
20:         "orders": "olist_orders_dataset.csv",
21:         "items": "olist_order_items_dataset.csv",
22:         "customers": "olist_customers_dataset.csv",
23:         "payments": "olist_order_payments_dataset.csv",
24:         "reviews": "olist_order_reviews_dataset.csv",
25:         "products": "olist_products_dataset.csv",
26:         "translation": "product_category_name_translation.csv"
27:     }
```
* **Lines 19-27**: Dictionary mapping short key names to actual CSV filenames.

```python
29:     datasets: dict[str, pd.DataFrame] = {}
30:     for key, filename in files.items():
31:         file_path = os.path.join(data_dir, filename)
32:         if not os.path.exists(file_path):
33:             raise FileNotFoundError(f"Required dataset file not found: {file_path}")
34:         datasets[key] = pd.read_csv(file_path)
35:     return datasets
```
* **Lines 29-35**: Loops through each filename, constructs full path safely with `os.path.join`, checks if file exists, reads CSV with `pd.read_csv()`, and stores in `datasets` dictionary.

```python
38: def load_and_clean_data(data_dir: str = "data/archive") -> pd.DataFrame:
```
* **Line 38**: Main ETL pipeline function returning a single combined DataFrame.

```python
47:     raw_data = load_raw_datasets(data_dir)
48:     orders_df = raw_data["orders"]
49:     items_df = raw_data["items"]
50:     customers_df = raw_data["customers"]
51:     payments_df = raw_data["payments"]
52:     reviews_df = raw_data["reviews"]
53:     products_df = raw_data["products"]
54:     translation_df = raw_data["translation"]
```
* **Lines 47-54**: Calls `load_raw_datasets` and unpacks individual DataFrames into local variables.

```python
57:     date_columns = [
58:         "order_purchase_timestamp",
59:         "order_approved_at",
60:         "order_delivered_carrier_date",
61:         "order_delivered_customer_date",
62:         "order_estimated_delivery_date"
63:     ]
64:     for col in date_columns:
65:         if col in orders_df.columns:
66:             orders_df[col] = pd.to_datetime(orders_df[col], errors="coerce")
```
* **Lines 57-66**: Converts string timestamp columns into actual datetime objects. `errors="coerce"` handles any corrupted dates by converting them to `NaT` (Not a Time).

```python
69:     products_translated = pd.merge(
70:         products_df,
71:         translation_df,
72:         on="product_category_name",
73:         how="left"
74:     )
75:     products_translated["product_category_name_english"] = (
76:         products_translated["product_category_name_english"]
77:         .fillna("others")
78:         .str.replace("_", " ")
79:         .str.title()
80:     )
```
* **Lines 69-80**: Merges product catalog with category translation table on `product_category_name`. Replaces missing values with `"others"`, converts underscores to spaces, and formats text to Title Case (e.g. `cama_mesa_banho` -> `Bed Bath Table`).

```python
83:     payment_agg = payments_df.groupby("order_id").agg(
84:         total_payment_value=("payment_value", "sum"),
85:         payment_type=("payment_type", lambda x: x.mode()[0] if not x.empty else "unknown"),
86:         payment_installments=("payment_installments", "max")
87:     ).reset_index()
```
* **Lines 83-87**: Aggregates payment records per `order_id` (since one order can have multiple payment installments). Calculates total paid value and primary payment method.

```python
90:     review_agg = reviews_df.groupby("order_id").agg(
91:         review_score=("review_score", "mean")
92:     ).reset_index()
```
* **Lines 90-92**: Aggregates customer review ratings per `order_id`.

```python
95:     df = orders_df.merge(customers_df, on="customer_id", how="inner")
96:     df = df.merge(items_df, on="order_id", how="inner")
97:     df = df.merge(products_translated[["product_id", "product_category_name_english"]], on="product_id", how="left")
98:     df = df.merge(payment_agg, on="order_id", how="left")
99:     df = df.merge(review_agg, on="order_id", how="left")
```
* **Lines 95-99**: Joins orders, customers, order items, translated products, payments, and reviews into one single master DataFrame `df`.

```python
102:    df["total_order_item_value"] = df["price"] + df["freight_value"]
103:    df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
104:    df["estimated_delivery_days"] = (df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]).dt.days
105:    df["is_delayed"] = (df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]).astype(int)
```
* **Lines 102-105**: Computes item-level revenue (`price + freight`), actual delivery days, estimated delivery days, and creates binary `is_delayed` flag (1 if late, 0 if on-time).

```python
108:    df["order_year"] = df["order_purchase_timestamp"].dt.year
109:    df["order_month"] = df["order_purchase_timestamp"].dt.month
110:    df["order_year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
111:    return df
```
* **Lines 108-111**: Extracts year, month, and year-month string (`YYYY-MM`) for monthly trend charting, then returns clean DataFrame.

---

### File 2: `src/metrics.py`

```python
11: def calculate_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
```
* **Line 11**: Function calculating high-level KPIs.

```python
21:     if df.empty:
22:         return { ... }
```
* **Lines 21-29**: Guard clause returning zero values if input DataFrame is empty.

```python
31:     total_revenue = float(df["price"].sum())
32:     total_orders = int(df["order_id"].nunique())
33:     total_customers = int(df["customer_unique_id"].nunique())
34:     avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
35:     avg_review = float(df["review_score"].dropna().mean()) if "review_score" in df.columns else 0.0
```
* **Lines 31-35**: Calculates sum of item prices, unique count of orders, unique customers, Average Order Value (AOV = Revenue / Orders), and mean customer review rating.

```python
38:     delivered_df = df[df["order_status"] == "delivered"]
39:     if not delivered_df.empty and "is_delayed" in delivered_df.columns:
40:         on_time_rate = float((1 - delivered_df["is_delayed"].mean()) * 100)
41:     else:
42:         on_time_rate = 0.0
```
* **Lines 38-42**: Filters for delivered orders and computes percentage of on-time deliveries (`1 - delayed_rate`).

```python
102: def calculate_rfm_segments(df: pd.DataFrame, snapshot_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
```
* **Line 102**: Performs Recency, Frequency, Monetary (RFM) customer segmentation.

```python
117:    rfm = df.groupby("customer_unique_id").agg(
118:        Recency=("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
119:        Frequency=("order_id", "nunique"),
120:        Monetary=("price", "sum")
121:    ).reset_index()
```
* **Lines 117-121**: Groups data by `customer_unique_id`. Calculates **Recency** (days since last purchase), **Frequency** (number of distinct orders), and **Monetary** (total spend).

```python
124:    rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop")
125:    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
126:    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
```
* **Lines 124-126**: Uses quantile binning (`pd.qcut`) to divide customers into 5 equal scoring groups (1 to 5). Note: For Recency, 5 is the best (most recent purchase). For Frequency/Monetary, 5 is the best (highest order count & spend).

```python
134:    def assign_segment(row: pd.Series) -> str:
135:        r, f = row["R_Score"], row["F_Score"]
136:        if r >= 4 and f >= 4:
137:            return "Champions"
138:        elif f >= 3 and r >= 3:
139:            return "Loyal Customers"
140:        elif r >= 4 and f <= 2:
141:            return "New / Recent Customers"
142:        elif r <= 2 and f >= 3:
143:            return "At Risk"
144:        elif r <= 2 and f <= 2:
145:            return "Lost Customers"
146:        else:
147:            return "Promising / Potential"
```
* **Lines 134-147**: Rule-based decision tree assigning human-interpretable customer personas based on R and F scores.

---

### File 3: `app.py`

```python
24: st.set_page_config(
25:     page_title="Retail Analytics Dashboard",
26:     page_icon="🛒",
27:     layout="wide",
28:     initial_sidebar_state="expanded"
29: )
```
* **Lines 24-29**: Configures Streamlit browser title, icon, and sets page to full wide layout mode.

```python
32: @st.cache_data(show_spinner="Loading and cleaning 100k+ order records...")
33: def get_dataset() -> pd.DataFrame:
34:     return load_and_clean_data(data_dir="data/archive")
```
* **Lines 32-34**: Decorates `get_dataset` with `@st.cache_data`. This caches the cleaned 100k+ record DataFrame in memory so page reloads are instantaneous without re-reading CSV files every time the user clicks a filter.

```python
37: def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
```
* **Line 37**: Renders interactive sidebar controls.

```python
49:     selected_dates = st.sidebar.date_input(
50:         "Select Purchase Date Range",
51:         value=(min_date, max_date),
52:         min_value=min_date,
53:         max_value=max_date
54:     )
```
* **Lines 49-54**: Date picker widget enabling user to select date range. Filters DataFrame by `order_purchase_timestamp`.

```python
67:     selected_states = st.sidebar.multiselect("Filter by Customer State", options=all_states, default=[])
```
* **Line 67**: Multi-select dropdown filtering by Brazilian customer state (e.g., SP, RJ, MG).

```python
106:    col1, col2, col3, col4, col5 = st.columns(5)
107:    col1.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
108:    col2.metric("Total Orders", f"{kpis['total_orders']:,}")
109:    col3.metric("Avg Order Value", f"${kpis['avg_order_value']:,.2f}")
110:    col4.metric("On-Time SLA Rate", f"{kpis['on_time_delivery_rate']}%")
111:    col5.metric("Avg Rating", f"{kpis['avg_review_score']} / 5.0")
```
* **Lines 106-111**: Displays 5 executive KPI visual metric cards at top of main page.

```python
116:    tab1, tab2, tab3, tab4, tab5 = st.tabs([
117:        "📊 Sales & Revenue Trends",
118:        "👥 Customer RFM Segmentation",
119:        "📦 Product & Category Analysis",
120:        "🚚 Logistics & Payments",
121:        "📋 Data Table & Export"
122:    ])
```
* **Lines 116-122**: Creates 5 main navigation tabs organizing dashboard views.

---

### File 4: `tests/test_metrics.py`

```python
17: @pytest.fixture
18: def sample_analytical_df() -> pd.DataFrame:
```
* **Lines 17-18**: Pytest fixture generating a small 4-row synthetic DataFrame to isolate unit testing without loading 100k CSV rows.

```python
45: def test_calculate_executive_kpis(sample_analytical_df: pd.DataFrame) -> None:
46:     kpis = calculate_executive_kpis(sample_analytical_df)
47:     assert kpis["total_revenue"] == 500.0
48:     assert kpis["total_orders"] == 4
49:     assert kpis["total_customers"] == 3
50:     assert kpis["avg_order_value"] == 125.0
51:     assert kpis["avg_review_score"] == 4.0
52:     assert kpis["on_time_delivery_rate"] == 75.0
```
* **Lines 45-52**: Unit test asserting that `calculate_executive_kpis` computes exact expected mathematical values.

---

## 💼 Section 5: Data Analyst Resume & Interview Talking Points

### 1. Resume Bullet Points (Copy & Paste to your Resume!)

* **E-Commerce Retail Analytics Dashboard**: Engineered an end-to-end Python & Streamlit analytics application processing **100,000+ relational e-commerce orders**, generating executive KPIs ($13.59M revenue, $137.75 AOV, 92.1% SLA rate).
* **Customer RFM Segmentation**: Implemented Recency, Frequency, Monetary (RFM) quantile segmentation in Pandas, categorizing **95,400+ customers** into behavioral personas and identifying **23.9% At-Risk customers** for targeted re-engagement.
* **Logistics & Delivery SLA Optimization**: Analyzed delivery timelines across 27 Brazilian states, uncovering delivery bottlenecks in northern regions (>20 days delivery SLA) and authoring unit-tested Python data pipelines using Pytest.

---

### 2. Top 5 Technical Interview Q&A

#### Q1: "How did you handle missing values or corrupted dates during data ingestion?"
> **Answer**: "When loading the raw Olist dataset in `src/data_loader.py`, I used Pandas `to_datetime` with `errors='coerce'`. This gracefully converted corrupted timestamp strings into `NaT` (Not a Time) values without crashing the pipeline. For missing product category translations, I filled null values with `'others'` using `.fillna('others')` and standardized category names to Title Case."

#### Q2: "Why did you split your project into `src/` modules instead of writing everything in a single Jupyter Notebook?"
> **Answer**: "Writing everything in a Jupyter Notebook makes code difficult to re-use, test, or deploy to production. By separating the ETL pipeline (`src/data_loader.py`), analytical business calculations (`src/metrics.py`), test suite (`tests/test_metrics.py`), and Streamlit UI (`app.py`), I maintained modular software architecture. This allowed me to write Pytest unit tests on core metric functions and cache data loading in Streamlit."

#### Q3: "How does your RFM Customer Segmentation logic work under the hood?"
> **Answer**: "In `src/metrics.py`, I grouped order data by `customer_unique_id` to aggregate Recency (days since last purchase relative to snapshot date), Frequency (total unique order count), and Monetary value (total merchandise spend). I then used Pandas `pd.qcut` quantile binning to assign scores from 1 to 5 for each metric. Finally, I mapped R and F scores into human-interpretable personas such as Champions (R>=4, F>=4), At-Risk (R<=2, F>=3), and Lost Customers."

#### Q4: "How did you optimize performance when filtering 100,000+ order rows in real-time on Streamlit?"
> **Answer**: "I leveraged Streamlit's `@st.cache_data` decorator on the `get_dataset()` function. This loads and cleans the CSV files once into in-memory memory cache when the app starts. When users interact with sidebar date pickers or state multi-select filters, Streamlit filters the already-cached DataFrame instantaneously without re-executing expensive disk reads or join operations."

#### Q5: "What key business recommendations would you present to executive stakeholders based on your analysis?"
> **Answer**: "Based on the dashboard insights: First, **Customer Retention**: 23.9% of customers are 'At-Risk' (historically valuable but inactive recently). Launching automated win-back email promotions can recover lost revenue. Second, **Logistics Bottlenecks**: Customers in remote northern states experience delivery lead times exceeding 20 days compared to 5 days in São Paulo. Establishing regional fulfillment centers in North/Northeast Brazil would improve delivery SLA and customer review scores."
