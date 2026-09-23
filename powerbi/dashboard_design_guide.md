# Power BI Dashboard Design Guide

Build the report from the published tables in `data/exports/`.

1. Executive Overview: KPI cards for revenue, profit, orders, customers, and margin; add a monthly revenue trend.
2. Sales Performance: compare `Sales_Channel`, `Region`, and monthly or quarterly sales.
3. Product Analytics: use category, subcategory, brand, revenue, units, and profit.
4. Customer Intelligence: use customer segments and customer revenue rankings.
5. Regional Analytics: map state and city sales, then compare regional margin.
6. Sales Representative: compare representative revenue, team, region, and target attainment from the Streamlit view.
7. AI Forecast: plot `forecast_date` against projected sales and confidence bounds from `sales_forecast`.
8. Business Insights: display severity, category, title, and insight from `business_insights`.
9. Anomaly Detection: filter `sales_anomalies` by `is_anomaly` and inspect sales, margin, and reason.

Use slicers for date, region, category, sales channel, and customer segment. Keep colors consistent across pages and show currency units in chart titles.
