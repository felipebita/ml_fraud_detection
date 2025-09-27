import pandas as pd

file_path = "/app/data/processed/processed_transactions.parquet"

try:
    df = pd.read_parquet(file_path)
    print("Successfully read the parquet file.")
    print("First 5 rows:")
    print(df.head())
except Exception as e:
    print(f"Error reading the parquet file: {e}")
