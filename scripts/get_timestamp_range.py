import pandas as pd

from src.utils.config import get_config

config = get_config()
processed_data_path = config["data"]["processed_path"]

df = pd.read_parquet(processed_data_path)

min_timestamp = df["event_timestamp"].min()
max_timestamp = df["event_timestamp"].max()

# Print in ISO 8601 format
print(f"min_timestamp={min_timestamp.isoformat()}")
print(f"max_timestamp={max_timestamp.isoformat()}")
