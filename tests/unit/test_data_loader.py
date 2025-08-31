# tests/data/test_data_loader.py

import pandas as pd
import pytest

# Adjust the import path based on your project structure
from src.data.data_loader import load_data

# A sample of valid data for testing
VALID_DATA = """step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud
1,PAYMENT,9839.64,C1231006815,170136.0,160296.36,M1979787155,0.0,0.0,0,0
1,TRANSFER,181.0,C1305486145,181.0,0.0,C553264065,0.0,0.0,1,0
"""


@pytest.fixture
def setup_raw_data_path(tmp_path, monkeypatch):
    """Creates a temporary 'raw' directory and sets the config path."""
    raw_path = tmp_path / "data" / "raw.csv"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    # Mock the config to return the temporary path
    monkeypatch.setattr(
        "src.data.data_loader.get_config",
        lambda: {"data": {"raw_path": str(raw_path)}},
    )
    return raw_path


def test_load_data_success(setup_raw_data_path):
    """Tests successful loading of a good CSV file."""
    file_path = setup_raw_data_path
    file_path.write_text(VALID_DATA)

    df = load_data()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "newbalanceOrig" in df.columns


def test_load_data_file_not_found(monkeypatch):
    """Tests that FileNotFoundError is raised for a non-existent file."""
    # Mock config to point to a non-existent file
    monkeypatch.setattr(
        "src.data.data_loader.get_config",
        lambda: {"data": {"raw_path": "non_existent_file.csv"}},
    )
    with pytest.raises(FileNotFoundError):
        load_data()


def test_load_data_empty_file(setup_raw_data_path):
    """Tests that ValueError is raised for an empty CSV file."""
    file_path = setup_raw_data_path
    file_path.touch()  # Create an empty file

    with pytest.raises(ValueError, match="Data file is empty"):
        load_data()
