from pathlib import Path

import pandas as pd


def create_dummy_data():
    """
    Creates a dummy processed_transactions.parquet file for CI/CD testing.
    This file contains the specific data points needed for the Feast integration tests.
    """
    data = {
        "event_timestamp": [pd.Timestamp("2024-01-01 01:00:00", tz="UTC")],
        "nameOrig": ["C1231006815"],
        "nameDest": ["M1979787155"],
        "type": ["PAYMENT"],
        "amount": [9839.64],
        "oldbalanceOrg": [170136.0],
        "newbalanceOrig": [160296.36],
        "oldbalanceDest": [0.0],
        "newbalanceDest": [0.0],
        "isFraud": [0],
        "isFlaggedFraud": [0],
    }
    df = pd.DataFrame(data)

    # Ensure correct data types
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
    df["amount"] = df["amount"].astype("float64")
    df["oldbalanceOrg"] = df["oldbalanceOrg"].astype("float64")
    df["newbalanceOrig"] = df["newbalanceOrig"].astype("float64")
    df["oldbalanceDest"] = df["oldbalanceDest"].astype("float64")
    df["newbalanceDest"] = df["newbalanceDest"].astype("float64")
    df["isFraud"] = df["isFraud"].astype("int64")
    df["isFlaggedFraud"] = df["isFlaggedFraud"].astype("int64")

    # Create the directory if it doesn't exist
    output_path = Path("data/processed")
    output_path.mkdir(parents=True, exist_ok=True)

    # Save the dummy data
    file_path = output_path / "processed_transactions.parquet"
    df.to_parquet(file_path)
    print(f"Dummy data created at {file_path}")


if __name__ == "__main__":
    create_dummy_data()
