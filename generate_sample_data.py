# Generates a deliberately messy sales dataset to demonstrate the
# cleaning pipeline: missing values, duplicates, inconsistent formats,
# whitespace issues, mixed casing, and outliers.

import numpy as np
import pandas as pd

np.random.seed(42)

n = 300

names = ["Alice Smith", "bob jones", "CAROL WHITE", "David  Lee", "eve brown",
         "Frank Miller", "Grace Wilson", "henry davis", "Ivy Taylor", "JACK MOORE"]
regions = ["North", "south", "EAST", "West ", " North", "east", "South", "WEST"]
categories = ["Electronics", "electronics", "Apparel", "APPAREL", "Home", "home ",
              "Sports", "sports", "Home Goods"]

rows = []
for i in range(n):
    row = {
        "order_id": f"ORD{1000+i}",
        "customer_name": np.random.choice(names),
        "region": np.random.choice(regions),
        "category": np.random.choice(categories),
        "quantity": np.random.randint(1, 20),
        "unit_price": round(np.random.uniform(5, 500), 2),
        "order_date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(np.random.randint(0, 365))),
    }
    rows.append(row)

df = pd.DataFrame(rows)
df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)

# --- Inject messiness ---

# 1. Missing values (random spread across several columns)
for col in ["unit_price", "region", "category", "quantity", "customer_name"]:
    idx = np.random.choice(df.index, size=int(n * 0.05), replace=False)
    df.loc[idx, col] = np.nan

# 2. Duplicate rows (exact copies)
dupes = df.sample(15, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

# 3. Inconsistent date formats (mix of string formats)
date_str = []
for d in df["order_date"]:
    if pd.isna(d):
        date_str.append(np.nan)
        continue
    fmt = np.random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d %b %Y"])
    date_str.append(d.strftime(fmt))
df["order_date"] = date_str

# 4. Negative / zero quantities (data entry errors)
err_idx = np.random.choice(df.index, size=8, replace=False)
df.loc[err_idx, "quantity"] = -1

# 5. Extreme outlier prices (typos like extra zero)
out_idx = np.random.choice(df.index, size=5, replace=False)
df.loc[out_idx, "unit_price"] = df.loc[out_idx, "unit_price"] * 100

# Recompute revenue to match the messy quantity/price (so revenue is also "dirty")
df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)

# Shuffle rows
df = df.sample(frac=1, random_state=2).reset_index(drop=True)

df.to_csv("raw_sales_data.csv", index=False)
print("Created raw_sales_data.csv with", len(df), "rows (messy version)")
print(df.head(10))
print("\nMissing values per column:")
print(df.isna().sum())
print("\nDuplicate rows:", df.duplicated().sum())
