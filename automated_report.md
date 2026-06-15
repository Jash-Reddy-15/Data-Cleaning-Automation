# Data Cleaning and Reporting - Automated Summary

## Cleaning Log

**PART 1: Generated messy sample dataset**

- Rows: 315 | Columns: 8

**PART 2: Initial data quality check**

- Missing in customer_name: 16
- Missing in region: 15
- Missing in category: 15
- Missing in quantity: 14
- Missing in unit_price: 15
- Missing in revenue: 28
- Fully identical rows: 4
- Duplicate order_id values: 15

**PART 3: Removing duplicates**

- Removed 15 duplicate order_id rows. New count: 300

**PART 4: Standardizing text fields**

- Regions standardized: ['East', 'North', 'South', 'West']
- Categories standardized: ['Apparel', 'Electronics', 'Home', 'Sports']
- Customer names cleaned: extra spaces removed, Title Case applied

**PART 5: Standardizing dates**

- All dates converted to YYYY-MM-DD format
- Unparseable dates: 0

**PART 6: Fixing data entry errors**

- Nulled 8 negative quantity values
- Price outlier bound: 755.7
- Found 4 outlier prices
- Outliers capped at 755.7

**PART 7: Handling missing values**

- quantity: filled 22 with median 10.0
- unit_price: filled 15 with median 269.54
- region: filled 15 with mode East
- category: filled 15 with mode Home
- customer_name: filled 15 with 'Unknown Customer'

**PART 8: Recalculating derived fields**

- Revenue recalculated as quantity * unit_price

**PART 9: Final quality check**

- Rows before: 315 | Rows after: 300
- Remaining missing values: 0
- Remaining duplicate order_ids: 0

**PART 10: Saved cleaned_sales_data.csv**


**PART 11: Summary statistics**

- Total revenue: 848686.25
- Total orders: 300
- Average order value: 2828.95
- Top region: East
- Top category: Home
- Saved 4 charts: revenue_by_region.png, revenue_by_category.png, monthly_revenue_trend.png, missing_values_comparison.png

## Key Metrics (Post-Cleaning)

| Metric | Value |
|---|---|
| Total Revenue | 848686.25 |
| Total Orders | 300 |
| Average Order Value | 2828.95 |
| Top Region | East |
| Top Category | Home |
| Duplicate Orders Removed | 15 |
| Rows Removed (bad dates) | 0 |
| Price Outliers Capped | 4 |

## Revenue by Region

- East: 276663.43
- South: 220980.75
- North: 191387.41
- West: 159654.66

## Revenue by Category

- Home: 293906.24
- Sports: 224721.27
- Apparel: 220329.93
- Electronics: 109728.81