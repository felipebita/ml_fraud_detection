# tests/unit/test_data_processing.py

import pandas as pd
import pytest

from src.data.data_processing import DataProcessor


@pytest.fixture
def processor():
    """Returns a DataProcessor instance."""
    return DataProcessor()


@pytest.fixture
def sample_df():
    """Returns a sample DataFrame for processing tests."""
    data = {
        "step": [1, 2, 3, 4],
        "type": ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN"],
        "amount": [100.0, 200.0, 50.0, 300.0],
    }
    return pd.DataFrame(data)


def test_standardize_converts_type_and_adds_timestamp(processor, sample_df):
    """
    Tests that the standardize method correctly converts column types
    and adds the 'event_timestamp' column.
    """
    standardized_df = processor.standardize(sample_df)

    # Test type conversion
    assert isinstance(standardized_df["type"].dtype, pd.CategoricalDtype)

    # Test for 'event_timestamp' column
    assert "event_timestamp" in standardized_df.columns
    assert pd.api.types.is_datetime64_any_dtype(standardized_df["event_timestamp"])

    # Test timestamp calculation
    start_date = pd.Timestamp("2024-01-01")
    expected_timestamps = start_date + pd.to_timedelta(sample_df["step"], unit="h")
    pd.testing.assert_series_equal(
        standardized_df["event_timestamp"],
        expected_timestamps,
        check_names=False,
    )


def test_filter_transaction_types(processor, sample_df):
    """
    Tests that the filter_transaction_types method correctly filters the DataFrame.
    """
    filtered_df = processor.filter_transaction_types(sample_df)
    expected_types = ["TRANSFER", "CASH_OUT"]
    assert all(item in expected_types for item in filtered_df["type"].unique())
    assert len(filtered_df) == 2


def test_encode_transaction_type(processor):
    """
    Tests that the encode_transaction_type method correctly encodes the 'type' column.
    """
    data = {
        "type": ["TRANSFER", "CASH_OUT"],
    }
    df = pd.DataFrame(data)
    encoded_df = processor.encode_transaction_type(df)
    assert encoded_df["type"].dtype == "int64"
    assert encoded_df["type"].tolist() == [1, 0]
