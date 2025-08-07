import boto3
import pandas as pd
import io

# AWS S3 Configuration
BUCKET_NAME = "data9bucket"
RAW_FILE_PATH = "raw_data/hopcoms_data.csv"
PROCESSED_FILE_PATH = "processed_data/processed_hopcoms_data.xlsx"

# Initialize S3 client
s3 = boto3.client("s3")

# Step 1: Download CSV from S3
obj = s3.get_object(Bucket=BUCKET_NAME, Key=RAW_FILE_PATH)
df = pd.read_csv(io.BytesIO(obj["Body"].read()))

# Debug: Print column names for verification
print("Available columns:", df.columns)

# Step 2: Data Cleaning (Handle Missing Values)
df = df.dropna()  # Remove rows with missing values

# Standardize column names (strip spaces, convert to lowercase)
df.columns = df.columns.str.strip()

# Rename columns to expected format
column_mapping = {
    "Price per kg": "Price",  # Rename to 'Price'
    "Total Price": "Total Revenue"  # Rename to 'Total Revenue'
}
df.rename(columns=column_mapping, inplace=True)

# Ensure required columns exist
expected_columns = ["Item Purchased", "Quantity Purchased", "Price", "Customer ID", "Category", "Total Revenue"]
for col in expected_columns:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}. Available columns: {df.columns}")

# Step 3: Business Insights
# 3.1 Top 10 Most Purchased Items
most_purchased = df.groupby("Item Purchased")["Quantity Purchased"].sum().reset_index()
most_purchased = most_purchased.sort_values(by="Quantity Purchased", ascending=False)
top_10_most_purchased = most_purchased.head(10)

# 3.2 Top 10 Least Purchased Items
least_purchased = most_purchased.tail(10)

# 3.3 Total Revenue Per Item
total_revenue_per_item = df.groupby("Item Purchased")["Total Revenue"].sum().reset_index()

# 3.4 Average Spending Per Customer
average_spending_per_customer = df.groupby("Customer ID")["Total Revenue"].sum().reset_index()

# 3.5 Category-wise Total Revenue
total_revenue_per_category = df.groupby("Category")["Total Revenue"].sum().reset_index()

# Step 4: Save Processed Data to Excel
processed_excel = io.BytesIO()

with pd.ExcelWriter(processed_excel, engine="xlsxwriter") as writer:
    top_10_most_purchased.to_excel(writer, sheet_name="Top 10 Most Purchased", index=False)
    least_purchased.to_excel(writer, sheet_name="Top 10 Least Purchased", index=False)
    total_revenue_per_item.to_excel(writer, sheet_name="Total Revenue Per Item", index=False)
    average_spending_per_customer.to_excel(writer, sheet_name="Avg Spending Per Customer", index=False)
    total_revenue_per_category.to_excel(writer, sheet_name="Revenue Per Category", index=False)
    writer.close()

processed_excel.seek(0)

# Step 5: Upload Processed File to S3
s3.put_object(Bucket=BUCKET_NAME, Key=PROCESSED_FILE_PATH, Body=processed_excel.getvalue())

print("Processing complete. Business insights saved and uploaded to S3.")





