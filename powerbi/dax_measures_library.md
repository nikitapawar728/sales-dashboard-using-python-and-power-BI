# DAX Measures Library

Create these measures on `fact_sales`.

```DAX
Total Revenue = SUM(fact_sales[Net_Sales])

Total Profit = SUM(fact_sales[Profit])

Total Orders = DISTINCTCOUNT(fact_sales[Order_ID])

Total Customers = DISTINCTCOUNT(fact_sales[Customer_ID])

Total Units = SUM(fact_sales[Quantity])

Average Order Value = DIVIDE([Total Revenue], [Total Orders])

Profit Margin % = DIVIDE([Total Profit], [Total Revenue])

Revenue per Customer = DIVIDE([Total Revenue], [Total Customers])

Order Count = COUNTROWS(fact_sales)
```

Format revenue and profit measures as currency, `Profit Margin %` as a percentage, and counts as whole numbers.
