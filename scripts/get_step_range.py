import pandas as pd

from src.utils.config import get_config

config = get_config()
processed_data_path = config["data"]["processed_path"]

df = pd.read_parquet(processed_data_path)

min_step = df["step"].min()
max_step = df["step"].max()

print(f"min_step={min_step}")
print(f"max_step={max_step}")
