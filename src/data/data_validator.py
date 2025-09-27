# src/data/data_validator.py

import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaError

from src.utils.logger import LoggerContext, get_logger

logger = get_logger(__name__)

# Define the Pandera schema for transaction data
transaction_schema = pa.DataFrameSchema(
    {
        "step": pa.Column(int, checks=pa.Check.ge(0), nullable=False),
        "type": pa.Column(
            str,
            checks=pa.Check.isin(
                ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]
            ),
            nullable=False,
        ),
        "amount": pa.Column(float, checks=pa.Check.ge(0.0), nullable=False),
        "nameOrig": pa.Column(str, nullable=False),
        "oldbalanceOrg": pa.Column(float, nullable=False),
        "newbalanceOrig": pa.Column(float, nullable=False),
        "nameDest": pa.Column(str, nullable=False),
        "oldbalanceDest": pa.Column(float, nullable=False),
        "newbalanceDest": pa.Column(float, nullable=False),
        "isFraud": pa.Column(int, checks=pa.Check.isin([0, 1]), nullable=False),
        "isFlaggedFraud": pa.Column(int, checks=pa.Check.isin([0, 1]), nullable=False),
    },
    strict=True,  # Ensures no extra columns are present
    coerce=True,  # Coerces data types to the specified types
)


class DataValidator:
    """
    A class to validate and standardize the transaction data using Pandera.
    """

    def __init__(self, schema: pa.DataFrameSchema = transaction_schema):
        """
        Initializes the DataValidator with a Pandera schema.

        Args:
            schema (pa.DataFrameSchema): The Pandera schema to use for validation.
        """
        self.schema = schema

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validates the input DataFrame against the Pandera schema.

        Args:
            df (pd.DataFrame): The DataFrame to validate.

        Returns:
            pd.DataFrame: The validated DataFrame.

        Raises:
            ValueError: If the DataFrame fails validation.
        """
        with LoggerContext(
            logger, "data_validation", num_rows=len(df), num_cols=len(df.columns)
        ) as log_context:
            try:
                validated_df: pd.DataFrame = self.schema.validate(df, lazy=False)
                log_context.context["status"] = "success"
                logger.info("Pandera validation completed successfully.")
                return validated_df
            except SchemaError as e:
                log_context.context["status"] = "failure"
                log_context.context["error_details"] = str(e)
                logger.error("Pandera validation failed.", error_details=e)
                # In a real pipeline, you might want to quarantine failing data
                # or handle this more gracefully than raising an error.
                raise ValueError(
                    "Data validation failed. Check logs for details."
                ) from e

    def standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes columns in the DataFrame.
        - Converts 'type' to a categorical type for efficiency.
        - Creates an 'event_timestamp' from the 'step' column.

        Args:
            df (pd.DataFrame): The DataFrame to standardize.

        Returns:
            pd.DataFrame: The standardized DataFrame.
        """
        logger.info("Data standardization started...")
        df_copy = df.copy()

        # Convert 'type' to a categorical type for efficiency
        df_copy["type"] = df_copy["type"].astype("category")

        # Create event_timestamp from 'step'
        # We assume 'step' represents hours from a starting point.
        start_date = pd.Timestamp("2024-01-01")
        df_copy["event_timestamp"] = start_date + pd.to_timedelta(
            df_copy["step"], unit="h"
        )

        logger.info("Data standardization completed.")
        return df_copy
