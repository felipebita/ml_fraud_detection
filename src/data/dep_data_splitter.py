"""
This script defines the DataSplitter class, which splits the processed data
into training and testing sets based on a chronological split.
"""

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.config import get_config
from src.utils.logger import get_logger

# Initialize a logger for this module
logger = get_logger(__name__)


class DataSplitter:
    """
    A class to split data into training and test sets based on time.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initializes the DataSplitter with configuration.

        Args:
            config: A dictionary containing the project configuration.
        """
        self.data_config = config["data"]
        self.split_config = config["data_splitting"]

        self.processed_path = Path(self.data_config["processed_path"])
        self.train_path = Path(self.data_config["train_dataset_path"])
        self.test_path = Path(self.data_config["test_dataset_path"])

        self.test_size: float = self.split_config["test_size"]
        self.timestamp_col: str = self.split_config["timestamp_col"]

    def split_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Loads, sorts, splits, and saves the data.

        Returns:
            A tuple containing the training and testing DataFrames.
        """
        logger.info(f"Loading processed data from '{self.processed_path}'...")
        try:
            df = pd.read_parquet(self.processed_path)
        except FileNotFoundError:
            logger.error(
                f"Source data file not found at '{self.processed_path}'. Aborting."
            )
            raise

        logger.info("Sorting data by timestamp to ensure chronological order.")
        df = df.sort_values(by=self.timestamp_col).reset_index(drop=True)

        split_index = int(len(df) * (1 - self.test_size))

        train_df = df.iloc[:split_index]
        test_df = df.iloc[split_index:]

        logger.info(
            f"Training set size: {len(train_df)} ({len(train_df) / len(df):.2%})"
        )
        logger.info(f"Test set size: {len(test_df)} ({len(test_df) / len(df):.2%})")

        # Ensure the destination directory exists
        self.train_path.parent.mkdir(parents=True, exist_ok=True)
        self.test_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving training set to '{self.train_path}'...")
        train_df.to_parquet(self.train_path)

        logger.info(f"Saving test set to '{self.test_path}'...")
        test_df.to_parquet(self.test_path)

        logger.info("Data splitting process completed successfully.")
        return train_df, test_df


def main() -> None:
    """
    Main function to instantiate and run the DataSplitter.
    """
    logger.info("--- Starting Data Splitting Pipeline ---")
    config = get_config()
    data_splitter = DataSplitter(config)
    data_splitter.split_data()
    logger.info("--- Data Splitting Pipeline Finished ---")


if __name__ == "__main__":
    main()
