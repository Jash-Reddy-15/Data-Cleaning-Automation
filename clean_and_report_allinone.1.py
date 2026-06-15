# Data Cleaning and Reporting Automation
# Single-file version - generates its own messy sample data,
# then cleans it and produces an automated report.
# Works on online compilers (no external CSV file needed).
# Requires: numpy, pandas, matplotlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

log = []

def note(msg):
    print(msg)
    log.append(msg)

# PART 1: GENERATE MESSY SAMPLE DATA
np.random.seed(42)
n = 300

names = ["Alice Smith", "bob jones", "CAROL WHITE", "David  Lee", "eve brown", "Frank Miller", "Grace Wilson", "henry davis", "Ivy Taylor", "JACK MOORE"]
regions = ["North", "south", "EAST", "West ", " North", "east", "South", "WEST"]
categories = ["Electronics", "electronics", "Apparel", "APPAREL", "Home", "home ", "Sports", "sports", "Home Goods"]

rows = []
for i in range(n):
    row = {
        "order_id": "ORD" + str(1000 + i),
        "customer_name": np.random.choice(names),
        "region": np.random.choice(regions),
        "category": np.random.choice(categories),
        "quantity": np.random.randint(1, 20),
        "unit_price": round(np.random.uniform(5, 500), 2),
        "order_date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(np.random.randint(0, 365)))
    }
    rows.append(row)

df = pd.DataFrame(rows)
df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)

for col in ["unit_price", "region", "category", "quantity", "customer_name"]:
    idx = np.random.choice(df.index, size=int(n * 0.05), replace=False)
    df.loc[idx, col] = np.nan

dupes = df.sample(15, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

date_str = []
for d in df["order_date"]:
    if pd.isna(d):
        date_str.append(np.nan)
    else:
        fmt_choice = np.random.choice(["A", "B", "C", "D"])
        if fmt_choice == "A":
            date_str.append(d.strftime("%Y-%m-%d"))
        elif fmt_choice == "B":
            date_str.append(d.strftime("%d/%m/%Y"))
        elif fmt_choice == "C":
            date_str.append(d.strftime("%m-%d-%Y"))
        else:
            date_str.append(d.strftime("%d %b %Y"))
df["order_date"] = date_str

err_idx = np.random.choice(df.index, size=8, replace=False)
df.loc[err_idx, "quantity"] = -1

out_idx = np.random.choice(df.index, size=5, replace=False)
df.loc[out_idx, "unit_price"] = df.loc[out_idx, "unit_price"] * 100

df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
df = df.sample(frac=1, random_state=2).reset_index(drop=True)

note("PART 1: Generated messy sample dataset")
note("  Rows: " + str(len(df)) + " | Columns: " + str(len(df.columns)))

# PART 2: INITIAL DATA QUALITY ASSESSMENT
note("\nPART 2: Initial data quality check")
missing_before = df.isna().sum()
for col in df.columns:
    if missing_before[col] > 0:
        note("  Missing in " + col + ": " + str(missing_before[col]))

dupes_full = df.duplicated().sum()
dupes_by_id = df.duplicated(subset=["order_id"]).sum()
note("  Fully identical rows: " + str(dupes_full))
note("  Duplicate order_id values: " + str(dupes_by_id))
rows_before = len(df)

# PART 3: REMOVE DUPLICATES
note("\nPART 3: Removing duplicates")
df = df.drop_duplicates(subset=["order_id"], keep="first").reset_index(drop=True)
note("  Removed " + str(dupes_by_id) + " duplicate order_id rows. New count: " + str(len(df)))

# PART 4: STANDARDIZE TEXT FIELDS
note("\nPART 4: Standardizing text fields")
df["region"] = df["region"].astype(str).str.strip().str.title()
df["region"] = df["region"].replace("Nan", np.nan)
note("  Regions standardized: " + str(sorted(df["region"].dropna().unique().tolist())))

df["category"] = df["category"].astype(str).str.strip().str.title()
df["category"] = df["category"].replace("Nan", np.nan)
df["category"] = df["category"].replace({"Home Goods": "Home"})
note("  Categories standardized: " + str(sorted(df["category"].dropna().unique().tolist())))

df["customer_name"] = df["customer_name"].astype(str).str.strip()
df["customer_name"] = df["customer_name"].str.replace(r"\s+", " ", regex=True)
df["customer_name"] = df["customer_name"].str.title()
df["customer_name"] = df["customer_name"].replace("Nan", np.nan)
note("  Customer names cleaned: extra spaces removed, Title Case applied")

# PART 5: STANDARDIZE DATES
note("\nPART 5: Standardizing dates")
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
note("  All dates converted to YYYY-MM-DD format")
note("  Unparseable dates: " + str(unparsed))

# PART 6: FIX DATA ENTRY ERRORS
note("\nPART 6: Fixing data entry errors")
neg_qty = (df["quantity"] < 0).sum()
df.loc[df["quantity"] < 0, "quantity"] = np.nan
note("  Nulled " + str(neg_qty) + " negative quantity values")

q1 = df["unit_price"].quantile(0.25)
q3 = df["unit_price"].quantile(0.75)
iqr = q3 - q1
upper_bound = q3 + 1.5 * iqr
outliers = (df["unit_price"] > upper_bound).sum()
note("  Price outlier bound: " + str(round(upper_bound, 2)))
note("  Found " + str(outliers) + " outlier prices")
df.loc[df["unit_price"] > upper_bound, "unit_price"] = upper_bound
note("  Outliers capped at " + str(round(upper_bound, 2)))

# PART 7: HANDLE MISSING VALUES
note("\nPART 7: Handling missing values")
for col in ["quantity", "unit_price"]:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        note("  " + col + ": filled " + str(n_missing) + " with median " + str(round(median_val, 2)))

for col in ["region", "category"]:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        mode_val = df[col].mode()[0]
        df[col] = df[col].fillna(mode_val)
        note("  " + col + ": filled " + str(n_missing) + " with mode " + mode_val)

n_missing_name = df["customer_name"].isna().sum()
if n_missing_name > 0:
    df["customer_name"] = df["customer_name"].fillna("Unknown Customer")
    note("  customer_name: filled " + str(n_missing_name) + " with 'Unknown Customer'")

n_missing_date = df["order_date"].isna().sum()
if n_missing_date > 0:
    df = df.dropna(subset=["order_date"]).reset_index(drop=True)
    note("  Dropped " + str(n_missing_date) + " rows with invalid dates")

# PART 8: RECALCULATE DERIVED FIELDS
note("\nPART 8: Recalculating derived fields")
df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
note("  Revenue recalculated as quantity * unit_price")

# PART 9: FINAL QUALITY CHECK
note("\nPART 9: Final quality check")
rows_after = len(df)
note("  Rows before: " + str(rows_before) + " | Rows after: " + str(rows_after))
note("  Remaining missing values: " + str(df.isna().sum().sum()))
note("  Remaining duplicate order_ids: " + str(df.duplicated(subset=["order_id"]).sum()))

coincidental = df.drop(columns=["order_id"]).duplicated().sum()
if coincidental > 0:
    note("  Note: " + str(coincidental) + " rows have identical attributes but different order_ids (kept as separate orders)")

# PART 10: SAVE CLEANED DATA
df.to_csv("cleaned_sales_data.csv", index=False)
note("\nPART 10: Saved cleaned_sales_data.csv")

# PART 11: SUMMARY STATISTICS
note("\nPART 11: Summary statistics")
total_revenue = df["revenue"].sum()
total_orders = len(df)
avg_order_value = df["revenue"].mean()
top_region = df.groupby("region")["revenue"].sum().idxmax()
top_category = df.groupby("category")["revenue"].sum().idxmax()

note("  Total revenue: " + str(round(total_revenue, 2)))
note("  Total orders: " + str(total_orders))
note("  Average order value: " + str(round(avg_order_value, 2)))
note("  Top region: " + top_region)
note("  Top category: " + top_category)

# PART 12: CHARTS
region_rev = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 4))
plt.bar(region_rev.index, region_rev.values, color="#378ADD")
plt.title("Revenue by Region (After Cleaning)")
plt.ylabel("Revenue")
plt.tight_layout()
plt.savefig("revenue_by_region.png", dpi=150)
plt.show()

cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 4))
plt.bar(cat_rev.index, cat_rev.values, color="#1D9E75")
plt.title("Revenue by Category (After Cleaning)")
plt.ylabel("Revenue")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("revenue_by_category.png", dpi=150)
plt.show()

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

missing_after = df.isna().sum()
cols_with_missing = missing_before[missing_before > 0].index.tolist()
before_vals = [missing_before[c] for c in cols_with_missing]
after_vals = [missing_after.get(c, 0) for c in cols_with_missing]
x = np.arange(len(cols_with_missing))
width = 0.35
plt.figure(figsize=(8, 4))
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

# PART 13: AUTOMATED MARKDOWN REPORT
report_lines = []
report_lines.append("# Data Cleaning and Reporting - Automated Summary")
report_lines.append("")
report_lines.append("## Cleaning Log")
report_lines.append("")

for i, line in enumerate(log):
    if line.startswith("\n"):
        line = line.strip()
    if line.startswith("PART"):
        if i > 0:
            report_lines.append("")
        report_lines.append("**" + line + "**")
        report_lines.append("")
    else:
        report_lines.append("- " + line.strip())

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
report_lines.append("| Duplicate Orders Removed | " + str(dupes_by_id) + " |")
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
note("\nDone. Cleaned data, charts, and report generated successfully.")
