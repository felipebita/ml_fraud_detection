import sys
from datetime import timedelta
from pathlib import Path

from feast import (
    Entity,
    FeatureView,
    Field,
    FileSource,
    ValueType,
)
from feast.data_format import ParquetFormat
from feast.types import Float64, Int64, String

from src.utils.config import get_config

# Get absolute path to project root
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Load the configuration
config = get_config()

# Get the path to the processed data from the config
processed_data_path = config["data"]["processed_path"]

# Use absolute path - this works regardless of CWD
file_path = str(project_root / processed_data_path)

print(f"DEBUG: Using file path: {file_path}")  # Temporary debug line

# Define entities
origin_customer = Entity(
    name="origin_customer", join_keys=["nameOrig"], value_type=ValueType.STRING
)
destination_customer = Entity(
    name="destination_customer", join_keys=["nameDest"], value_type=ValueType.STRING
)

# Define the data source
transactions_source = FileSource(
    path=file_path, timestamp_field="event_timestamp", file_format=ParquetFormat()
)

# Define a feature view for transaction features
transaction_features = FeatureView(
    name="transaction_features",
    entities=[origin_customer, destination_customer],
    ttl=timedelta(days=365),
    schema=[
        Field(name="type", dtype=String),
        Field(name="amount", dtype=Float64),
        Field(name="oldbalanceOrg", dtype=Float64),
        Field(name="newbalanceOrig", dtype=Float64),
        Field(name="oldbalanceDest", dtype=Float64),
        Field(name="newbalanceDest", dtype=Float64),
        Field(name="isFraud", dtype=Int64),
        Field(name="isFlaggedFraud", dtype=Int64),
    ],
    source=transactions_source,
)
