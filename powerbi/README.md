# Power BI Integration

The dashboard publishes Power BI-ready data to `data/exports/` and refreshes `database/sales_analytics.db` at startup.

## Recommended connection

1. Run `streamlit run app.py --server.port 8501` once to refresh the assets.
2. In Power BI Desktop, choose **Get data > Text/CSV**.
3. Import the CSV files from `data/exports/`.
4. For a relational source, choose **Get data > SQLite database** and select `database/sales_analytics.db`.
5. Use `data_model_guide.md` to create relationships and `dax_measures_library.md` for measures.

## Published tables

- `fact_sales.csv` / `fact_sales`
- `customer_segments.csv` / `customer_segments`
- `sales_forecast.csv` / `sales_forecast`
- `forecast_model_metrics.csv` / `forecast_model_metrics`
- `sales_anomalies.csv` / `sales_anomalies`
- `business_insights.csv` / `business_insights`

If an ML dataset is empty, the file still has a canonical header. Run the ETL pipeline to populate forecast, anomaly, segment, and insight records.
