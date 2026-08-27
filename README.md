# 🛒 Executive Retail Analytics Dashboard & RFM Segmentation

A production-ready E-Commerce Executive Analytics Dashboard built with Python, Pandas, Plotly, Streamlit, and Pytest using real-world data from 100,000+ Brazilian e-commerce orders (Olist Dataset).

---

## 🌟 Executive Summary & Key Business Insights

- **Total Revenue & Volume**: Processed **$13.59M** in gross merchandise revenue across **98,666 orders** and **95,420 unique customers** ($137.75 Average Order Value).
- **Customer Segmentation (RFM)**: Identified **16.0% Champions** ($1.2M+ spend) and flagged **23.9% At-Risk Customers** for automated win-back campaigns.
- **Top Product Categories**: *Health Beauty* ($1.25M), *Watches Gifts* ($1.20M), and *Bed Bath Table* ($1.03M) represent the top revenue drivers.
- **Logistics & Delivery SLA**: Maintained a **92.1% On-Time Delivery Rate**, while identifying key delivery delays in remote northern states (e.g., RR, AP) averaging >20 days delivery time.

---

## 🛠️ Technology Stack

- **Data Wrangling & ETL**: Python 3.12, Pandas, NumPy
- **Business Analytics & Metrics**: Custom modular Python engine (`src/metrics.py`)
- **Data Visualization & UI**: Streamlit, Plotly Express & Graph Objects
- **Testing & Quality Assurance**: Pytest (100% unit test coverage on analytics functions)

---

## 📂 Project Architecture

```
retail-analytics-dashboard/
├── data/archive/                      # Raw Olist CSV relational tables
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_products_dataset.csv
│   └── product_category_name_translation.csv
├── src/                               # Core Python Package
│   ├── __init__.py
│   ├── data_loader.py                 # Data ETL pipeline (loads, cleans, merges tables)
│   └── metrics.py                     # Business metrics (KPIs, Monthly Trends, RFM, SLA)
├── tests/                             # Test Suite
│   ├── __init__.py
│   └── test_metrics.py                # Pytest unit tests for business logic
├── app.py                             # Interactive Streamlit Web Dashboard
├── analysis.py                        # CLI Analysis Runner Script
├── requirement.txt                    # Project Dependencies
├── README.md                          # Portfolio Showcase Documentation
└── PROJECT_GUIDE.md                   # Comprehensive Tutorial & Line-by-Line Guide
```

---

## 🚀 Getting Started

### 1. Prerequisites & Installation
Ensure you have Python 3.10+ installed. Clone this repository and install dependencies:

```bash
pip install -r requirement.txt
```

### 2. Run CLI Executive Summary Report
To run the automated ETL pipeline and output executive summary statistics in your terminal:

```bash
python analysis.py
```

### 3. Run Automated Unit Tests
To execute the Pytest test suite validating metric computations:

```bash
pytest
```

### 4. Launch Interactive Web Dashboard
To open the interactive Streamlit web dashboard in your browser:

```bash
streamlit run app.py
```

---

## 🎓 Learning & Interview Preparation

For a complete tutorial explaining every concept with real-world analogies, file interconnections, line-by-line code breakdowns, and interview talking points, refer to [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md).
