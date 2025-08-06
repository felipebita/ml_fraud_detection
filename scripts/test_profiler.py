# scripts/test_profiler.py
"""Test the data profiler with sample data."""
import numpy as np
import pandas as pd

from src.data.data_profiler import quick_profile

# Create sample fraud detection data
np.random.seed(42)
n_samples = 10000

df = pd.DataFrame(
    {
        "transaction_id": range(n_samples),
        "amount": np.random.lognormal(3, 1.5, n_samples),
        "merchant_id": np.random.choice(
            ["M001", "M002", "M003", "M004", "M005"], n_samples
        ),
        "customer_id": np.random.choice(range(1000), n_samples),
        "timestamp": pd.date_range("2024-01-01", periods=n_samples, freq="5min"),
        "is_fraud": np.random.choice([0, 1], n_samples, p=[0.98, 0.02]),
    }
)

# Add some data quality issues
df.loc[100:200, "amount"] = np.nan  # Missing values
df.loc[500:600, "merchant_id"] = None  # More missing values

# Run profiler
profile = quick_profile(df, export_path="data/profiling_results.json")
