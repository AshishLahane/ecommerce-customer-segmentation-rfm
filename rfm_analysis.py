import pandas as pd
import numpy as np

# 1. Download and read dataset from verified public GitHub mirror
print("Downloading online retail dataset...")
url = "https://raw.githubusercontent.com/datasets/online-retail-dataset/master/data/online_retail.csv"

try:
    df = pd.read_csv(url, encoding='ISO-8859-1')
except Exception:
    alt_url = "https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/07_Visualization/Online_Retail/Online_Retail.csv"
    df = pd.read_csv(alt_url, encoding='ISO-8859-1')

print("Loaded successfully! Total records:", len(df))

# Standardize column naming
df.columns = [c.strip() for c in df.columns]
col_mapping = {
    'Invoice': 'InvoiceNo',
    'Customer ID': 'CustomerID',
    'Price': 'UnitPrice'
}
df.rename(columns=col_mapping, inplace=True)

# 2. Clean Data
print("Cleaning data...")
df_clean = df[
    (df['CustomerID'].notnull()) & 
    (df['Quantity'] > 0) & 
    (df['UnitPrice'] > 0)
].copy()

df_clean['TotalRevenue'] = df_clean['Quantity'] * df_clean['UnitPrice']
df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])

# 3. Calculate RFM Metrics
print("Calculating RFM scores...")
snapshot_date = df_clean['InvoiceDate'].max() + pd.Timedelta(days=1)

rfm = df_clean.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'nunique',
    'TotalRevenue': 'sum'
}).reset_index()

rfm.rename(columns={
    'InvoiceDate': 'Recency',
    'InvoiceNo': 'Frequency',
    'TotalRevenue': 'Monetary'
}, inplace=True)

# 4. Quartile Scoring (1 to 4)
rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])

# 5. Cohort Segmentation
def assign_segment(row):
    r = int(row['R_Score'])
    f = int(row['F_Score'])
    if r == 4 and f >= 3:
        return 'Champions / VIP'
    elif r >= 3:
        return 'Loyal Customers'
    elif r <= 2 and f >= 3:
        return 'At Risk'
    else:
        return 'Standard / Inactive'

rfm['Segment'] = rfm.apply(assign_segment, axis=1)

# 6. Save the Output File
output_file = 'customer_rfm_segments.csv'
rfm.to_csv(output_file, index=False)
print(f"Done! '{output_file}' generated successfully with {len(rfm)} customers.")
