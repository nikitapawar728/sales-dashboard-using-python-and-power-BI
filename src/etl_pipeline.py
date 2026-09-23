"""Refresh dashboard outputs and Power BI import assets."""

from config import ensure_demo_data, ensure_demo_ml_outputs, ensure_power_bi_assets


def main():
    ensure_demo_data()
    ensure_demo_ml_outputs()
    ensure_power_bi_assets()
    print("ETL pipeline completed successfully.")
    print("Business insights: data/processed/business_insights.csv")
    print("Power BI exports: data/exports/")
    print("SQLite database: database/sales_analytics.db")


if __name__ == "__main__":
    main()
