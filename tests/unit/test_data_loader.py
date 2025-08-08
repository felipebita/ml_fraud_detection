# tests/data/test_data_loader.py

import pandas as pd
import pytest
from pydantic import ValidationError

# Adjust the import path based on your project structure
from src.data.data_loader import TransactionSchema, load_data

# A sample of valid data for testing
VALID_DATA = """step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud
1,PAYMENT,9839.64,C1231006815,170136.0,160296.36,M1979787155,0.0,0.0,0,0
1,TRANSFER,181.0,C1305486145,181.0,0.0,C553264065,0.0,0.0,1,0
"""

# Data with schema violations (e.g., 'amount' is a string)
INVALID_DATA = """step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud
1,PAYMENT,not_a_float,C1231006815,170136.0,160296.36,M1979787155,0.0,0.0,0,0
"""

# Data with a mix of valid and invalid rows
MIXED_DATA = VALID_DATA + INVALID_DATA


@pytest.fixture
def setup_raw_data_path(tmp_path, monkeypatch):
    """Creates a temporary 'raw' directory and sets the env var."""
    raw_path = tmp_path / "data" / "raw"
    raw_path.mkdir(parents=True)
    monkeypatch.setenv("RAW_DATA_PATH", str(raw_path))
    return raw_path


def test_load_data_success(setup_raw_data_path):
    """Tests successful loading and validation of a good CSV file."""
    raw_path = setup_raw_data_path
    file_path = raw_path / "raw.csv"
    file_path.write_text(VALID_DATA)

    df = load_data(file_name="raw.csv")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "newbalanceOrig" in df.columns
    # Check if Pydantic correctly cast types
    assert df["amount"].dtype == "float64"


def test_load_data_file_not_found():
    """Tests that FileNotFoundError is raised for a non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_data(file_name="non_existent_file.csv")


def test_load_data_empty_file(setup_raw_data_path):
    """Tests that ValueError is raised for an empty CSV file."""
    raw_path = setup_raw_data_path
    file_path = raw_path / "raw.csv"
    file_path.touch()  # Create an empty file

    with pytest.raises(ValueError, match="Data file is empty"):
        load_data(file_name="raw.csv")


def test_load_data_with_invalid_rows_are_skipped(setup_raw_data_path):
    """Tests that invalid rows are skipped and valid ones are loaded."""
    raw_path = setup_raw_data_path
    file_path = raw_path / "raw.csv"
    file_path.write_text(MIXED_DATA)

    df = load_data(file_name="raw.csv")

    # Should only contain the 2 valid rows
    assert len(df) == 2
    assert df["isFraud"].sum() == 1


def test_load_data_all_invalid_rows(setup_raw_data_path):
    """Tests that an error is raised if no rows are valid."""
    raw_path = setup_raw_data_path
    file_path = raw_path / "raw.csv"
    file_path.write_text(INVALID_DATA)

    with pytest.raises(ValueError, match="No valid transaction data found"):
        load_data(file_name="raw.csv")


def test_transaction_schema_validation():
    """Directly tests the Pydantic schema."""
    # Valid case
    valid_dict = {
        "step": 1,
        "type": "CASH_IN",
        "amount": 100.0,
        "nameOrig": "C1",
        "oldbalanceOrg": 0.0,
        "newbalanceOrig": 100.0,
        "nameDest": "C2",
        "oldbalanceDest": 50.0,
        "newbalanceDest": 150.0,
        "isFraud": 0,
        "isFlaggedFraud": 0,
    }
    # This should not raise an error
    TransactionSchema(**valid_dict)

    # Invalid case (wrong type)
    invalid_dict = valid_dict.copy()
    invalid_dict["step"] = "one"  # Should be int

    with pytest.raises(ValidationError):
        TransactionSchema(**invalid_dict)
