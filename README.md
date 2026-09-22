# 📊 Advanced Sales Analytics & Business Intelligence Dashboard

> **End-to-End Enterprise Data Engineering, Machine Learning & Power BI Platform**  
> *MSc IT Academic Thesis — University of Mumbai*

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-SQLite%20%7C%20MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Web_App-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.x-013243?style=for-the-badge&logo=numpy&logoColor=white)

---

## 🎯 Project Overview

Organizations struggle with **siloed, raw sales data** that cannot answer critical business questions:
- *Which customers are high-value champions vs. churn risks?*
- *What will revenue look like over the next 90 days?*
- *Which products drive profits vs. erode margins?*
- *Are there anomalous transactions indicating fraud or data errors?*

This project delivers a **complete, production-grade Business Intelligence platform** that:

✅ Processes **25,000+ sales transactions** across 15+ Indian states  
✅ Builds a **Star Schema** relational database (1 Fact + 7 Dimension tables)  
✅ Trains **K-Means RFM clustering** to segment 1,500 customers into 5 personas  
✅ Benchmarks **4 ML models** for 30/60/90-day sales forecasting  
✅ Runs **Isolation Forest anomaly detection** flagging 750 suspicious transactions  
✅ Visualizes everything in a **9-page interactive Power BI dashboard**  
✅ Includes a live **Streamlit web management portal**  
✅ Executes end-to-end in **~35 seconds**

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                  │
│          Raw CSV / Excel Sales Transactions                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              PYTHON DATA ENGINEERING LAYER                       │
│  • Deduplication & Missing Value Imputation                      │
│  • IQR Outlier Handling & Accounting Validation                  │
│  • Star Schema Dimensional Normalization                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  K-Means RFM │ │ Time-    │ │  Isolation   │
│  Customer    │ │ Series   │ │  Forest      │
│  Segmentation│ │ Forecast │ │  Anomaly Det.│
└──────┬───────┘ └────┬─────┘ └──────┬───────┘
       │              │              │
       └──────────────┼──────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              SQL DATABASE (Star Schema)                          │
│  fact_sales + dim_customer + dim_product + dim_date + ...        │
│  + ml_customer_segments + ml_sales_forecast + ml_anomalies       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│  Power BI        │    │  Streamlit       │
│  9-Page Dashboard│    │  Web Portal      │
│  + 40 DAX Measures│   │  (localhost:8501) │
└──────────────────┘    └──────────────────┘
```

---

## 📂 Project Structure

```
sales-analytics-dashboard/
│
├── 📁 data/
│   ├── raw/                          # Raw incoming CSV/Excel files
│   ├── processed/                    # Cleaned Star Schema CSVs & ML outputs
│   └── exports/                      # Ready-to-import Power BI CSV files
│
├── 📁 database/
│   ├── schema.sql                    # ANSI-SQL DDL for Star Schema & Views
│   ├── connection.py                 # SQLAlchemy connection manager
│   ├── db_loader.py                  # Automated SQL ingestion & verification
│   └── sales_analytics.db           # SQLite database (14 MB)
│
├── 📁 src/
│   ├── config.py                     # Central config, paths & hyperparameters
│   ├── data_generator.py            # Realistic 25,000+ transaction generator
│   ├── data_cleaning.py             # Cleaning, validation & Star Schema builder
│   ├── rfm_segmentation.py          # RFM scoring & K-Means clustering engine
│   ├── sales_forecasting.py         # Multi-model ML forecasting (RF, GBR, Ridge, LR)
│   ├── anomaly_detection.py         # Isolation Forest anomaly detection
│   ├── business_insights.py         # Automated diagnostic insight engine
│   └── etl_pipeline.py              # Master 7-stage pipeline orchestrator
│
├── 📁 web_app/
│   └── app.py                        # 9-page Streamlit analytics portal
│
├── 📁 powerbi/
│   ├── dax_measures_library.md       # 40+ production DAX formulas
│   ├── data_model_guide.md           # Star Schema relationship blueprint
│   └── dashboard_design_guide.md     # Complete step-by-step build guide
│
├── 📁 docs/
│   ├── MSC_PROJECT_REPORT.md         # Full academic dissertation & Viva Q&A
│   ├── Sales_Analytics_Project_Report.pdf  # Official PDF report
│   └── RESUME_PORTFOLIO_GUIDE.md     # Resume bullets & interview guide
│
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## ⚡ Quick Start Guide

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/sales-analytics-dashboard.git
cd sales-analytics-dashboard
pip install -r requirements.txt
```

### 2. Run the Full ETL + ML Pipeline
```bash
python src/etl_pipeline.py
```
This generates data, cleans it, trains ML models, and loads everything into the database in ~35 seconds.

### 3. Launch the Streamlit Web Dashboard
```bash
streamlit run web_app/app.py
```
Open `http://localhost:8501` in your browser.

### 4. Build the Power BI Dashboard
1. Open **Power BI Desktop**
2. **Get Data** → **Text/CSV** → import all files from `data/exports/`
3. Follow the step-by-step [Dashboard Design Guide](powerbi/dashboard_design_guide.md)
4. Copy DAX formulas from [DAX Measures Library](powerbi/dax_measures_library.md)

---

## 📊 Power BI Dashboard Pages (9 Pages)

| # | Page | Key Visuals |
|---|------|-------------|
| 1 | **Executive Overview** | Revenue/Profit/Orders KPI cards, Monthly trend combo chart, Regional donut, Top/Bottom 10 products |
| 2 | **Sales Performance** | Channel-wise revenue, Quarterly YoY comparison, Daily sales velocity area chart |
| 3 | **Product Analytics** | Category stacked bars, Brand treemap, Profitability scatter quadrant |
| 4 | **Customer Intelligence** | RFM K-Means segment donut, Customer detail table, Retention metrics |
| 5 | **Regional Analytics** | India state filled map, Top 10 states bar chart, City performance heatmap |
| 6 | **Sales Representative** | Rep revenue bar chart, Team performance scorecard table |
| 7 | **AI Sales Forecast** | 30/60/90-day forecast line chart with confidence bands, Model benchmark table |
| 8 | **Business Insights** | Automated AI-generated diagnostic insights with severity indicators |
| 9 | **Anomaly Detection** | Anomaly scatter plot, Flagged transactions audit table (Isolation Forest) |

---

## 🤖 Machine Learning Models

### 1. Customer RFM Segmentation (K-Means Clustering)
- **Algorithm**: K-Means with log1p transformation + StandardScaler
- **Features**: Recency, Frequency, Monetary (RFM)
- **Clusters**: 5 customer personas
- **Silhouette Score**: 0.2493

| Persona | Count | Revenue Share | Strategy |
|---------|-------|---------------|----------|
| 👑 Champions | 286 (19.1%) | ₹124.53 Cr (29.9%) | VIP perks, loyalty rewards |
| 🤝 Loyal | 397 (26.5%) | ₹118.05 Cr (28.4%) | Cross-sell, volume rebates |
| 🌟 Potential Loyalists | 312 (20.8%) | ₹84.52 Cr (20.3%) | Onboarding campaigns |
| ⚠️ At Risk | 343 (22.9%) | ₹76.51 Cr (18.4%) | Win-back campaigns |
| 💤 Lost/Inactive | 162 (10.8%) | ₹12.11 Cr (2.9%) | Low-cost remarketing |

### 2. Time-Series Sales Forecasting
- **Models Benchmarked**: Random Forest, Gradient Boosting, Ridge Regression, Linear Regression
- **Features**: Cyclical sin/cos encodings, lag features (t-1, t-7, t-14, t-30), rolling averages
- **Output**: 30/60/90-day projections with 95% confidence intervals

### 3. Anomaly Detection (Isolation Forest)
- **Algorithm**: Isolation Forest (n_estimators=150, contamination=3%)
- **Anomalies Flagged**: 750 transactions
- **Detection Targets**: Excessive discounts, bulk volume spikes, negative margin leaks

---

## 📈 Key Business Metrics

| Metric | Value |
|--------|-------|
| Total Revenue | ₹415.72 Crores |
| Total Profit | ₹93.36 Crores |
| Profit Margin | 22.46% |
| Total Orders | 14,317 |
| Unique Customers | 1,500 |
| Pipeline Execution Time | 34.42 seconds |

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Programming** | Python 3.11 |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | Scikit-Learn (K-Means, Random Forest, Gradient Boosting, Ridge, Isolation Forest) |
| **Database** | SQLite / MySQL, SQLAlchemy |
| **Visualization** | Microsoft Power BI (40+ DAX measures), Plotly |
| **Web Application** | Streamlit |
| **PDF Generation** | ReportLab |

---

## 🎓 Academic Documentation

This project was developed as part of the **MSc IT (Part 2)** curriculum at the **University of Mumbai**.

- 📄 [Full Project Report (PDF)](docs/Sales_Analytics_Project_Report.pdf)
- 📝 [Complete Dissertation (Markdown)](docs/MSC_PROJECT_REPORT.md)
- 💼 [Resume & Portfolio Guide](docs/RESUME_PORTFOLIO_GUIDE.md)

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).

---

## 👤 Author

**Nikita Sharma**  
MSc IT — University of Mumbai  
G. M. Vedak College of Science, Tala, Raigad

---

⭐ **If you found this project helpful, please give it a star!**
