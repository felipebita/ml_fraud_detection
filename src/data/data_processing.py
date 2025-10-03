# src/data/data_processing.py

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """
    A class for processing and transforming transaction data.
    """

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

    def filter_transaction_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters the DataFrame to include only specified transaction types.

        Args:
            df (pd.DataFrame): The DataFrame to filter.

        Returns:
            pd.DataFrame: The filtered DataFrame.
        """
        logger.info("Filtering transaction types...")
        allowed_types = ["CASH_OUT", "TRANSFER"]
        filtered_df = df[df["type"].isin(allowed_types)].copy()
        logger.info(f"Data filtered to include only: {allowed_types}")
        return filtered_df

    def encode_transaction_type(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Encodes the 'type' column into a binary format.

        Args:
            df (pd.DataFrame): The DataFrame to process.

        Returns:
            pd.DataFrame: The DataFrame with the encoded 'type' column.
        """
        logger.info("Encoding transaction type...")
        df_copy = df.copy()
        df_copy["type"] = df_copy["type"].apply(lambda x: 1 if x == "TRANSFER" else 0)
        logger.info("Transaction type encoded successfully.")
        return df_copy

    def convert_int_to_float(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts integer columns to float.

        Args:
            df (pd.DataFrame): The DataFrame to process.

        Returns:
            pd.DataFrame: The DataFrame with integer columns converted to float.
        """
        logger.info("Converting integer columns to float...")
        df_copy = df.copy()
        for col in df_copy.select_dtypes(include="integer").columns:
            df_copy[col] = df_copy[col].astype(float)
        logger.info("Integer columns converted to float successfully.")
        return df_copy
