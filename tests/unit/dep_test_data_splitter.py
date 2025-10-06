"""
Unit tests for the DataSplitter class.
"""

from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from src.data.dep_data_splitter import DataSplitter


@pytest.fixture
def mock_config() -> dict[str, Any]:
    """Provides a mock configuration for tests."""
    return {
        "data": {
            "processed_path": "dummy/processed.parquet",
            "train_dataset_path": "dummy/train.parquet",
            "test_dataset_path": "dummy/test.parquet",
        },
        "data_splitting": {
            "test_size": 0.2,
            "timestamp_col": "step",
        },
    }


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Creates a sample DataFrame for testing."""
    # Create a DataFrame with 10 rows, out of chronological order
    data = {
        "step": [5, 2, 8, 1, 9, 4, 7, 3, 10, 6],
        "feature": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    }
    return pd.DataFrame(data)


def test_data_splitter_logic(
    mock_config: dict[str, Any], sample_dataframe: pd.DataFrame, mocker: Any
) -> None:
    """
    Tests the core logic of the DataSplitter class.

    It verifies that the data is read, sorted, split chronologically, and
    saved correctly.
    """
    # Mock the pandas file operations
    mocker.patch("pandas.read_parquet", return_value=sample_dataframe)
    mock_to_parquet = mocker.patch("pandas.DataFrame.to_parquet")

    # Instantiate and run the splitter, capturing the returned dataframes
    splitter = DataSplitter(config=mock_config)
    train_df, test_df = splitter.split_data()

    # 1. Verify the split ratio on the returned dataframes
    assert len(train_df) == 8, "Train set should have 8 rows (80% of 10)."
    assert len(test_df) == 2, "Test set should have 2 rows (20% of 10)."

    # 2. Verify the chronological split on the returned dataframes
    assert train_df["step"].max() == 8, "Max step in train set should be 8."
    assert test_df["step"].min() == 9, "Min step in test set should be 9."
    assert (
        train_df["step"].max() < test_df["step"].min()
    ), "The latest training data must be earlier than the earliest test data."

    # 3. Verify that the to_parquet method was called correctly
    assert mock_to_parquet.call_count == 2, "Expected to_parquet to be called twice."

    # 4. Check the paths the data was saved to (as positional arguments)
    train_call_args = mock_to_parquet.call_args_list[0]
    test_call_args = mock_to_parquet.call_args_list[1]

    saved_train_path = train_call_args.args[0]
    saved_test_path = test_call_args.args[0]

    expected_train_path = Path(mock_config["data"]["train_dataset_path"])
    expected_test_path = Path(mock_config["data"]["test_dataset_path"])

    assert saved_train_path == expected_train_path
    assert saved_test_path == expected_test_path
