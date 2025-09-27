from datetime import timedelta

from feast import (
    Entity,
    FeatureView,
    Field,
    FileSource,
    ValueType,
)
from feast.data_format import ParquetFormat
from feast.types import Float64, Int64, String

# The complex path resolution logic that was here previously was causing issues during
# the Feast Feature Store initialization.
#
# Reverting to the simpler, relative path that is known to work as per the summary
# in `project_development/LAST_SESSION.md`.
#
# The path is relative to the project root, which is the context from which `feast`
# commands are executed.

# Define entities
origin_customer = Entity(
    name="origin_customer", join_keys=["nameOrig"], value_type=ValueType.STRING
)
destination_customer = Entity(
    name="destination_customer", join_keys=["nameDest"], value_type=ValueType.STRING
)

# Define the data source
transactions_source = FileSource(
    path="./data/processed/processed_transactions.parquet",
    timestamp_field="event_timestamp",
    file_format=ParquetFormat(),
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
