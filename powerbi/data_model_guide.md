# Power BI Data Model Guide

## Core table

Use `fact_sales` as the primary transaction table. Its transaction key is `Order_ID`.

Recommended dimensions can be built from distinct columns in `fact_sales`:

- `dim_date`: `Order_Date`, `Year`, `Quarter`, `Month`, `Month_Name`
- `dim_product`: `Product_ID`, `Product_Name`, `Category`, `SubCategory`, `Brand`
- `dim_customer`: `Customer_ID`, `Customer_Name`, `Customer_Segment`, `City`, `State`
- `dim_region`: `Region`, `State`, `City`
- `dim_sales_rep`: `Sales_Representative`, `Sales_Team`, `Region`

## Relationships

Create one-to-many, single-direction relationships from each dimension to `fact_sales`:

- `dim_date[Order_Date]` -> `fact_sales[Order_Date]`
- `dim_product[Product_ID]` -> `fact_sales[Product_ID]`
- `dim_customer[Customer_ID]` -> `fact_sales[Customer_ID]`
- `dim_region[Region]` -> `fact_sales[Region]`
- `dim_sales_rep[Sales_Representative]` -> `fact_sales[Sales_Representative]`

Keep the ML tables disconnected unless a visual explicitly needs them. Use `Customer_ID`, `forecast_date`, or `Order_ID` as visual-level fields when comparing results.

Set `Order_Date` and `forecast_date` to Date types. Set revenue, profit, and forecast values to Decimal Number or Fixed Decimal Number.
