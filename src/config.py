from pathlib import Path
import re
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
DATABASE_DIR = BASE_DIR / "database"
SALES_DATABASE_FILE = DATABASE_DIR / "sales_analytics.db"

for directory in (DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR, DATABASE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# Common dataset filenames used by the dashboard.
MASTER_SALES_FILE = PROCESSED_DATA_DIR / "cleaned_sales_master.csv"
RFM_SEGMENTS_FILE = PROCESSED_DATA_DIR / "ml_customer_segments.csv"
FORECAST_FILE = PROCESSED_DATA_DIR / "ml_sales_forecast.csv"
MODEL_METRICS_FILE = PROCESSED_DATA_DIR / "forecast_model_metrics.csv"
ANOMALIES_FILE = PROCESSED_DATA_DIR / "ml_sales_anomalies.csv"
INSIGHTS_FILE = PROCESSED_DATA_DIR / "business_insights.csv"

POWER_BI_DATASETS = {
    "fact_sales": MASTER_SALES_FILE,
    "customer_segments": RFM_SEGMENTS_FILE,
    "sales_forecast": FORECAST_FILE,
    "forecast_model_metrics": MODEL_METRICS_FILE,
    "sales_anomalies": ANOMALIES_FILE,
    "business_insights": INSIGHTS_FILE,
}

SALES_REQUIRED_COLUMNS = [
    "Order_ID",
    "Customer_ID",
    "Customer_Name",
    "Product_ID",
    "Product_Name",
    "Category",
    "SubCategory",
    "Order_Date",
    "Region",
    "State",
    "City",
    "Sales_Channel",
    "Sales_Representative",
    "Sales_Team",
    "Quantity",
    "Unit_Price",
    "Discount_Pct",
    "Net_Sales",
    "Profit",
    "Profit_Margin_Pct",
    "Payment_Method",
    "Customer_Segment",
    "Brand",
    "is_anomaly",
    "anomaly_reason",
]


def ensure_csv_header(path, columns):
    """Create a canonical header when a generated CSV is missing or blank."""
    try:
        existing_columns = pd.read_csv(path, nrows=0).columns.tolist()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        existing_columns = []
    if not existing_columns:
        pd.DataFrame(columns=columns).to_csv(path, index=False)


def ensure_demo_data():
    """Create a sample sales dataset covering every column the dashboard expects."""
    empty_files = [
        (RFM_SEGMENTS_FILE, ["Segment_Label", "Customer_ID", "Monetary", "Frequency"]),
        (FORECAST_FILE, [
            "is_forecast", "forecast_date", "projected_sales", "actual_sales",
            "lower_confidence_bound", "upper_confidence_bound"
        ]),
        (MODEL_METRICS_FILE, ["model_name", "mae", "rmse", "r2"]),
        (ANOMALIES_FILE, [
            "is_anomaly", "Net_Sales", "Profit_Margin_Pct", "Order_ID",
            "Product_Name", "anomaly_reason", "Order_Date", "Customer_Name",
            "Quantity", "Discount_Pct", "Profit"
        ]),
        (INSIGHTS_FILE, ["Severity", "Category", "Title", "Insight"]),
    ]
    if MASTER_SALES_FILE.exists() and MASTER_SALES_FILE.stat().st_size > 0:
        for path, columns in empty_files:
            ensure_csv_header(path, columns)
        return

    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=45, freq="D")
    products = [
        ("P-1001", "Aero Wireless Headphones", "Electronics", "Audio", "Echo", 5999, 12),
        ("P-1002", "Urban Smart Watch", "Electronics", "Wearables", "Nova", 4499, 15),
        ("P-1003", "Classic Office Chair", "Furniture", "Seating", "Orbit", 7999, 10),
        ("P-1004", "PureClean Vacuum", "Home", "Appliances", "CleanPro", 12999, 18),
        ("P-1005", "Trail Running Shoes", "Apparel", "Footwear", "Summit", 3999, 20),
    ]
    customers = [f"Customer {i}" for i in range(1, 21)]
    reps = [
        ("R-01", "North Team"), ("R-02", "North Team"), ("R-03", "South Team"),
        ("R-04", "West Team"), ("R-05", "East Team"), ("R-06", "Central Team"),
    ]
    regions = [
        ("North", "Punjab", "Chandigarh"),
        ("South", "Tamil Nadu", "Chennai"),
        ("East", "West Bengal", "Kolkata"),
        ("West", "Maharashtra", "Mumbai"),
    ]

    rows = []
    for idx, dt in enumerate(dates, start=1):
        product = products[(idx - 1) % len(products)]
        customer_name = customers[(idx - 1) % len(customers)]
        rep_name, team = reps[(idx - 1) % len(reps)]
        region_name, state, city = regions[(idx - 1) % len(regions)]
        quantity = 2 + ((idx * 3) % 9)
        unit_price = product[5]
        discount_pct = 5 + ((idx * 7) % 15)
        gross = quantity * unit_price
        net = round(gross * (1 - discount_pct / 100), 2)
        profit = round(net * 0.22, 2)
        rows.append({
            "Order_ID": f"ORD-{idx:04d}",
            "Customer_ID": f"CUST-{(idx % 20) + 1:03d}",
            "Customer_Name": customer_name,
            "Product_ID": product[0],
            "Product_Name": product[1],
            "Category": product[2],
            "SubCategory": product[3],
            "Order_Date": dt.strftime("%Y-%m-%d"),
            "Region": region_name,
            "State": state,
            "City": city,
            "Sales_Channel": ["Online", "Retail", "Distributor"][idx % 3],
            "Sales_Representative": rep_name,
            "Sales_Team": team,
            "Quantity": quantity,
            "Unit_Price": unit_price,
            "Discount_Pct": discount_pct,
            "Net_Sales": net,
            "Profit": profit,
            "Profit_Margin_Pct": round((profit / net * 100) if net else 0, 2),
            "Payment_Method": ["UPI", "Credit Card", "Net Banking"][idx % 3],
            "Customer_Segment": ["Loyal", "New", "VIP"][idx % 3],
            "Brand": product[4],
            "is_anomaly": False,
            "anomaly_reason": "",
        })

    demo_df = pd.DataFrame(rows)
    for col in SALES_REQUIRED_COLUMNS:
        if col not in demo_df.columns:
            demo_df[col] = ""
    demo_df = demo_df[SALES_REQUIRED_COLUMNS]
    demo_df.to_csv(MASTER_SALES_FILE, index=False)

    for path, columns in empty_files:
        ensure_csv_header(path, columns)


def ensure_power_bi_assets():
    """Export processed datasets to CSV and refresh the Power BI SQLite source."""
    export_paths = []
    for table_name, source_path in POWER_BI_DATASETS.items():
        if not source_path.exists():
            continue
        export_path = EXPORTS_DIR / f"{table_name}.csv"
        try:
            dataset = pd.read_csv(source_path)
        except pd.errors.EmptyDataError:
            dataset = pd.DataFrame()
        dataset.to_csv(export_path, index=False)
        export_paths.append((table_name, source_path))

    with sqlite3.connect(SALES_DATABASE_FILE) as connection:
        for table_name, source_path in export_paths:
            safe_table_name = re.sub(r"[^a-zA-Z0-9_]", "_", table_name)
            try:
                dataset = pd.read_csv(source_path)
            except pd.errors.EmptyDataError:
                dataset = pd.DataFrame()
            if dataset.empty and len(dataset.columns) == 0:
                dataset = pd.DataFrame({"record_id": pd.Series(dtype="int64")})
            dataset.to_sql(
                safe_table_name,
                connection,
                if_exists="replace",
                index=False,
            )
