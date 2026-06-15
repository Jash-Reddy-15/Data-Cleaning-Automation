# Data Cleaning & Reporting Automation

An automated pipeline that takes a messy, real-world-style sales dataset and produces a clean dataset, summary statistics, visual reports, and a markdown audit log — all in one run.

## What This Project Does

1. **Generates a realistic messy dataset** (or load your own CSV) containing:
   - Missing values across multiple columns
   - Duplicate records (same `order_id` entered twice)
   - Inconsistent text casing/whitespace (`"bob jones"`, `"CAROL WHITE"`, `"David  Lee"`)
   - Inconsistent region/category naming (`"south"`, `"EAST"`, `"West "`, `"Home Goods"` vs `"Home"`)
   - Multiple date formats mixed together (`2024-01-05`, `05/01/2024`, `01-05-2024`, `5 Jan 2024`)
   - Data entry errors (negative quantities)
   - Price outliers (typos like an extra zero)

2. **Cleans the data step by step**, logging every action:
   - Removes true duplicates (matched on `order_id`)
   - Standardizes text fields (Title Case, trimmed whitespace, merged category names)
   - Parses all date formats into one consistent `YYYY-MM-DD` format
   - Nulls invalid negative quantities, then imputes
   - Detects price outliers via the IQR method and caps them (winsorization)
   - Fills missing numeric values with median, categorical with mode
   - Recalculates derived fields (`revenue = quantity * unit_price`) for consistency

3. **Generates an automated report**:
   - `cleaned_sales_data.csv` — the clean dataset
   - `automated_report.md` — full step-by-step cleaning log + key metrics table
   - 4 charts: revenue by region, revenue by category, monthly revenue trend, and a before/after missing-values comparison

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core language |
| pandas / numpy | Data cleaning & transformation |
| matplotlib | Visual reports |

## How to Run

**Option A — Single file (recommended, works on any online compiler):**
```bash
python clean_and_report_allinone.py
```
This generates its own sample data and runs the full pipeline — no input file needed.

**Option B — Two-step (separate data generation):**
```bash
python generate_sample_data.py   # creates raw_sales_data.csv
python clean_and_report.py       # cleans it and generates reports
```

Requires only `pandas`, `numpy`, `matplotlib` — all standard, pre-installed on most environments.

## Output Files

| File | Description |
|---|---|
| `cleaned_sales_data.csv` | Fully cleaned dataset, ready for analysis |
| `automated_report.md` | Step-by-step cleaning log + summary metrics table |
| `revenue_by_region.png` | Bar chart of revenue by region |
| `revenue_by_category.png` | Bar chart of revenue by category |
| `monthly_revenue_trend.png` | Line chart of revenue over time |
| `missing_values_comparison.png` | Before vs. after missing-value counts per column |

## Example Cleaning Results

| Metric | Value |
|---|---|
| Rows before cleaning | 315 |
| Rows after cleaning | 300 |
| Duplicate orders removed | 15 |
| Negative quantities fixed | 8 |
| Price outliers capped | 4 |
| Remaining missing values | 0 |

## Using Your Own Data

Replace the data-generation section with:

```python
df = pd.read_csv("your_file.csv")
```

Then adjust column names in the cleaning steps to match your dataset (e.g. rename `order_date`, `region`, `category`, etc. as needed).

## Excel / Power BI Alternative

The same workflow maps to Excel/Power BI:
- **Power Query** → Remove Duplicates, Trim/Clean text transforms, Change Data Type for dates, Replace Errors/Outliers
- **Power Pivot / DAX** → recalculate revenue measures
- **Power BI dashboard** → load `cleaned_sales_data.csv`, build the same 4 visuals (bar charts, line chart, before/after comparison) using slicers for region/category

## Learning Outcomes

- Identifying and handling missing data (deletion vs. imputation)
- Deduplication strategies (exact match vs. business-key match)
- Standardizing inconsistent categorical and date data
- Outlier detection with the IQR method and winsorization
- Building a repeatable, auditable cleaning pipeline
- Automated reporting for stakeholder communication

## License

MIT — free to use, modify, and distribute.
# Data-Cleaning-Automation
# Data-Cleaning-Automation
