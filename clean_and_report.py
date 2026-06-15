# Data Cleaning & Reporting Automation
# ======================================
# Automated pipeline that:
#  1. Loads raw (messy) data
#  2. Cleans it - missing values, duplicates, inconsistent text/dates, outliers
#  3. Logs every cleaning action taken (for transparency/audit)
#  4. Generates summary statistics and visual reports
#  5. Saves cleaned data + an automated text/markdown report
#
# Run: python clean_and_report.py
# Requires: pandas, numpy, matplotlib (all standard)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

log = []

def note(msg):
    print(msg)
    log.append(msg)

# ----------------------------------------------------------------------
# 1. LOAD DATA
# ----------------------------------------------------------------------
# Replace with your own file: df = pd.read_csv("your_data.csv")
df = pd.read_csv("raw_sales_data.csv")
note("STEP 1: Loaded raw_sales_data.csv")
note("  Rows: " + str(len(df)) + " | Columns: " + str(len(df.columns)))
rows_before = len(df)

# ----------------------------------------------------------------------
# 2. INITIAL DATA QUALITY ASSESSMENT
# ----------------------------------------------------------------------
note("\nSTEP 2: Initial data quality check")
missing_before = df.isna().sum()
note("  Missing values per column:")
for col in df.columns:
    if missing_before[col] > 0:
        note("    " + col + ": " + str(missing_before[col]))

dupes_full = df.duplicated().sum()
dupes_by_id = df.duplicated(subset=["order_id"]).sum()
note("  Fully identical rows (including order_id): " + str(dupes_full))
note("  Duplicate order_id values: " + str(dupes_by_id))

# ----------------------------------------------------------------------
# 3. REMOVE DUPLICATES
# ----------------------------------------------------------------------
note("\nSTEP 3: Removing duplicate rows")
# Duplicate order_id is the reliable signal of a true duplicate record
# (same order entered twice). Keep the first occurrence.
df = df.drop_duplicates(subset=["order_id"], keep="first").reset_index(drop=True)
note("  Removed " + str(dupes_by_id) + " rows with duplicate order_id. New row count: " + str(len(df)))

# ----------------------------------------------------------------------
# 4. STANDARDIZE TEXT FIELDS (region, category, customer_name)
# ----------------------------------------------------------------------
note("\nSTEP 4: Standardizing text fields")

# Strip whitespace and fix casing for region
df["region"] = df["region"].astype(str).str.strip().str.title()
df["region"] = df["region"].replace("Nan", np.nan)
note("  Region values standardized to Title Case, whitespace stripped")
note("  Unique regions now: " + str(sorted(df["region"].dropna().unique().tolist())))

# Strip whitespace and fix casing for category, merge similar categories
df["category"] = df["category"].astype(str).str.strip().str.title()
df["category"] = df["category"].replace("Nan", np.nan)
df["category"] = df["category"].replace({"Home Goods": "Home"})
note("  Category values standardized to Title Case, 'Home Goods' merged into 'Home'")
note("  Unique categories now: " + str(sorted(df["category"].dropna().unique().tolist())))

# Standardize customer names: strip extra whitespace, title case
df["customer_name"] = df["customer_name"].astype(str).str.strip()
df["customer_name"] = df["customer_name"].str.replace(r"\s+", " ", regex=True)
df["customer_name"] = df["customer_name"].str.title()
df["customer_name"] = df["customer_name"].replace("Nan", np.nan)
note("  Customer names: extra spaces collapsed, Title Case applied")

# ----------------------------------------------------------------------
# 5. STANDARDIZE DATE FORMATS
# ----------------------------------------------------------------------
note("\nSTEP 5: Standardizing date formats")
# Multiple formats present (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY, "DD Mon YYYY")
# Try a list of known formats and parse whichever matches.

known_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d %b %Y"]

def parse_date(val):
    if pd.isna(val):
        return np.nan
    for fmt in known_formats:
        try:
            return pd.to_datetime(val, format=fmt)
        except ValueError:
            continue
    return pd.to_datetime(val, errors="coerce")

df["order_date"] = df["order_date"].apply(parse_date)
unparsed = df["order_date"].isna().sum()
note("  Dates parsed into a single datetime format (YYYY-MM-DD)")
note("  Dates that could not be parsed: " + str(unparsed))

# ----------------------------------------------------------------------
# 6. FIX DATA ENTRY ERRORS (negative/zero quantities, extreme price outliers)
# ----------------------------------------------------------------------
note("\nSTEP 6: Fixing data entry errors")

neg_qty = (df["quantity"] < 0).sum()
df.loc[df["quantity"] < 0, "quantity"] = np.nan
note("  Found and nulled " + str(neg_qty) + " rows with negative quantity (data entry errors)")

# Detect price outliers using IQR method
q1 = df["unit_price"].quantile(0.25)
q3 = df["unit_price"].quantile(0.75)
iqr = q3 - q1
upper_bound = q3 + 1.5 * iqr
outliers = (df["unit_price"] > upper_bound).sum()
note("  Unit price IQR bounds: up to " + str(round(upper_bound, 2)))
note("  Found " + str(outliers) + " price outliers above this bound (likely typos, e.g. extra zero)")

# Cap outliers at the upper bound rather than dropping rows
df.loc[df["unit_price"] > upper_bound, "unit_price"] = upper_bound
note("  Outlier prices capped at " + str(round(upper_bound, 2)) + " (winsorization)")

# ----------------------------------------------------------------------
# 7. HANDLE MISSING VALUES
# ----------------------------------------------------------------------
note("\nSTEP 7: Handling missing values")

# Numeric columns: fill with median (robust to outliers)
for col in ["quantity", "unit_price"]:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        note("  " + col + ": filled " + str(n_missing) + " missing values with median (" + str(round(median_val, 2)) + ")")

# Categorical columns: fill with mode (most frequent value)
for col in ["region", "category"]:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        mode_val = df[col].mode()[0]
        df[col] = df[col].fillna(mode_val)
        note("  " + col + ": filled " + str(n_missing) + " missing values with mode (" + mode_val + ")")

# Customer name: fill with placeholder (can't guess a name)
n_missing_name = df["customer_name"].isna().sum()
if n_missing_name > 0:
    df["customer_name"] = df["customer_name"].fillna("Unknown Customer")
    note("  customer_name: filled " + str(n_missing_name) + " missing values with 'Unknown Customer'")

# Dates: drop rows where date is missing/unparseable (can't impute meaningfully)
n_missing_date = df["order_date"].isna().sum()
if n_missing_date > 0:
    df = df.dropna(subset=["order_date"]).reset_index(drop=True)
    note("  order_date: dropped " + str(n_missing_date) + " rows with missing/invalid dates")

# ----------------------------------------------------------------------
# 8. RECALCULATE DERIVED FIELDS
# ----------------------------------------------------------------------
note("\nSTEP 8: Recalculating derived fields")
df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
note("  Revenue recalculated as quantity * unit_price for consistency")

# ----------------------------------------------------------------------
# 9. FINAL DATA QUALITY CHECK
# ----------------------------------------------------------------------
note("\nSTEP 9: Final data quality check")
rows_after = len(df)
note("  Rows before cleaning: " + str(rows_before))
note("  Rows after cleaning: " + str(rows_after))
note("  Remaining missing values: " + str(df.isna().sum().sum()))
note("  Remaining duplicate order_ids: " + str(df.duplicated(subset=["order_id"]).sum()))

coincidental = df.drop(columns=["order_id"]).duplicated().sum()
if coincidental > 0:
    note("  Note: " + str(coincidental) + " rows share identical attribute values "
         "(customer, region, category, qty, price, date) but have distinct order_ids. "
         "These are treated as separate legitimate orders, not duplicates.")

# ----------------------------------------------------------------------
# 10. SAVE CLEANED DATA
# ----------------------------------------------------------------------
df.to_csv("cleaned_sales_data.csv", index=False)
note("\nSTEP 10: Saved cleaned data to cleaned_sales_data.csv")

# ----------------------------------------------------------------------
# 11. SUMMARY STATISTICS
# ----------------------------------------------------------------------
note("\nSTEP 11: Summary statistics")
total_revenue = df["revenue"].sum()
total_orders = len(df)
avg_order_value = df["revenue"].mean()
top_region = df.groupby("region")["revenue"].sum().idxmax()
top_category = df.groupby("category")["revenue"].sum().idxmax()

note("  Total revenue: " + str(round(total_revenue, 2)))
note("  Total orders: " + str(total_orders))
note("  Average order value: " + str(round(avg_order_value, 2)))
note("  Top region by revenue: " + top_region)
note("  Top category by revenue: " + top_category)

# ----------------------------------------------------------------------
# 12. VISUAL SUMMARY REPORT
# ----------------------------------------------------------------------

# Revenue by region
region_rev = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 4))
plt.bar(region_rev.index, region_rev.values, color="#378ADD")
plt.title("Revenue by Region (After Cleaning)")
plt.ylabel("Revenue")
plt.tight_layout()
plt.savefig("revenue_by_region.png", dpi=150)
plt.show()

# Revenue by category
cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 4))
plt.bar(cat_rev.index, cat_rev.values, color="#1D9E75")
plt.title("Revenue by Category (After Cleaning)")
plt.ylabel("Revenue")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("revenue_by_category.png", dpi=150)
plt.show()

# Revenue trend over time (monthly)
df["month"] = df["order_date"].dt.to_period("M").astype(str)
monthly_rev = df.groupby("month")["revenue"].sum()
plt.figure(figsize=(10, 4))
plt.plot(monthly_rev.index, monthly_rev.values, marker="o", color="#D4537E")
plt.title("Monthly Revenue Trend (After Cleaning)")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("monthly_revenue_trend.png", dpi=150)
plt.show()

# Before/after comparison: missing values per column
missing_after = df.isna().sum()
plt.figure(figsize=(8, 4))
cols_with_missing = missing_before[missing_before > 0].index.tolist()
before_vals = [missing_before[c] for c in cols_with_missing]
after_vals = [missing_after.get(c, 0) for c in cols_with_missing]
x = np.arange(len(cols_with_missing))
width = 0.35
plt.bar(x - width/2, before_vals, width, label="Before cleaning", color="#A32D2D")
plt.bar(x + width/2, after_vals, width, label="After cleaning", color="#3B6D11")
plt.xticks(x, cols_with_missing, rotation=20)
plt.title("Missing Values: Before vs After Cleaning")
plt.ylabel("Count")
plt.legend()
plt.tight_layout()
plt.savefig("missing_values_comparison.png", dpi=150)
plt.show()

note("\nSaved 4 charts: revenue_by_region.png, revenue_by_category.png, monthly_revenue_trend.png, missing_values_comparison.png")

# ----------------------------------------------------------------------
# 13. WRITE AUTOMATED MARKDOWN REPORT
# ----------------------------------------------------------------------
report_lines = []
report_lines.append("# Data Cleaning & Reporting - Automated Summary")
report_lines.append("")
report_lines.append("## Cleaning Log")
report_lines.append("")
for line in log:
    report_lines.append("- " + line if not line.startswith("\n") else "\n- " + line.strip())
report_lines.append("")
report_lines.append("## Key Metrics (Post-Cleaning)")
report_lines.append("")
report_lines.append("| Metric | Value |")
report_lines.append("|---|---|")
report_lines.append("| Total Revenue | " + str(round(total_revenue, 2)) + " |")
report_lines.append("| Total Orders | " + str(total_orders) + " |")
report_lines.append("| Average Order Value | " + str(round(avg_order_value, 2)) + " |")
report_lines.append("| Top Region | " + top_region + " |")
report_lines.append("| Top Category | " + top_category + " |")
report_lines.append("| Rows Removed (duplicate order_id) | " + str(dupes_by_id) + " |")
report_lines.append("| Rows Removed (bad dates) | " + str(n_missing_date) + " |")
report_lines.append("| Price Outliers Capped | " + str(outliers) + " |")
report_lines.append("")
report_lines.append("## Revenue by Region")
report_lines.append("")
for region, rev in region_rev.items():
    report_lines.append("- " + region + ": " + str(round(rev, 2)))
report_lines.append("")
report_lines.append("## Revenue by Category")
report_lines.append("")
for cat, rev in cat_rev.items():
    report_lines.append("- " + cat + ": " + str(round(rev, 2)))

with open("automated_report.md", "w") as f:
    f.write("\n".join(report_lines))

note("\nSaved automated_report.md")
note("\nDone. All cleaned data, charts, and report generated successfully.")
