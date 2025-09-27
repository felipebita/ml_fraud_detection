# tests/unit/test_data_validator.py

import pandas as pd
import pytest

from src.data.data_validator import DataValidator, transaction_schema


@pytest.fixture
def validator():
    """Returns a DataValidator instance."""
    return DataValidator(schema=transaction_schema)


@pytest.fixture
def valid_df():
    """Returns a DataFrame that is valid according to the schema."""
    data = {
        "step": [1, 2],
        "type": ["PAYMENT", "TRANSFER"],
        "amount": [100.0, 200.0],
        "nameOrig": ["C1", "C2"],
        "oldbalanceOrg": [1000.0, 2000.0],
        "newbalanceOrig": [900.0, 1800.0],
        "nameDest": ["M1", "C3"],
        "oldbalanceDest": [0.0, 500.0],
        "newbalanceDest": [100.0, 700.0],
        "isFraud": [0, 1],
        "isFlaggedFraud": [0, 0],
    }
    return pd.DataFrame(data)


def test_validate_success(validator, valid_df):
    """Tests that a valid DataFrame passes validation."""
    validated_df = validator.validate(valid_df)
    assert isinstance(validated_df, pd.DataFrame)
    assert validated_df.equals(valid_df)


def test_validate_invalid_type_raises_value_error(validator, valid_df):
    """Tests that validation fails for a column with a non-coercible data type."""
    invalid_df = valid_df.copy()
    invalid_df["amount"] = "not_a_float"

    with pytest.raises(ValueError):
        validator.validate(invalid_df)


def test_validate_coerces_types(validator, valid_df):
    """Tests that the validator correctly coerces data types."""
    invalid_df = valid_df.copy()
    invalid_df["amount"] = "100.50"
    invalid_df["step"] = "1"

    validated_df = validator.validate(invalid_df)
    assert validated_df["amount"].dtype == "float64"
    assert validated_df["step"].dtype == "int64"


def test_validate_out_of_range_value(validator, valid_df):
    """Tests that validation fails for a value outside the allowed range."""
    invalid_df = valid_df.copy()
    invalid_df.loc[0, "amount"] = -100.0  # amount must be >= 0

    with pytest.raises(ValueError):
        validator.validate(invalid_df)


def test_validate_disallowed_category(validator, valid_df):
    """Tests that validation fails for a disallowed categorical value."""
    invalid_df = valid_df.copy()
    invalid_df.loc[0, "type"] = "REFUND"  # Not in the allowed list

    with pytest.raises(ValueError):
        validator.validate(invalid_df)


def test_validate_missing_column(validator, valid_df):
    """Tests that validation fails if a required column is missing."""
    invalid_df = valid_df.drop(columns=["isFraud"])

    with pytest.raises(ValueError):
        validator.validate(invalid_df)


def test_validate_extra_column(validator, valid_df):
    """Tests that validation fails if there is an extra column (strict=True)."""
    invalid_df = valid_df.copy()
    invalid_df["extra_col"] = "some_data"

    with pytest.raises(ValueError):
        validator.validate(invalid_df)


def test_standardize_converts_type_and_adds_timestamp(validator, valid_df):
    """
    Tests that the standardize method correctly converts column types
    and adds the 'event_timestamp' column.
    """
    standardized_df = validator.standardize(valid_df)

    # Test type conversion
    assert isinstance(standardized_df["type"].dtype, pd.CategoricalDtype)

    # Test for 'event_timestamp' column
    assert "event_timestamp" in standardized_df.columns
    assert pd.api.types.is_datetime64_any_dtype(standardized_df["event_timestamp"])

    # Test timestamp calculation
    start_date = pd.Timestamp("2024-01-01")
    expected_timestamps = start_date + pd.to_timedelta(valid_df["step"], unit="h")
    pd.testing.assert_series_equal(
        standardized_df["event_timestamp"],
        expected_timestamps,
        check_names=False,
    )
