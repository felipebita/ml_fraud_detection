# tests/conftest.py
import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def temp_dir():
    """Temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_mlflow_config(temp_dir):
    """Mock MLflow configuration for testing."""
    return {
        "db_path": str(temp_dir / "test_mlflow.db"),
        "default_artifact_root": str(temp_dir / "artifacts"),
        "experiment_name": "test_experiment",
    }


@pytest.fixture
def sample_experiment_data():
    """Sample MLflow experiment data for analytics testing."""
    return pd.DataFrame(
        {
            "run_id": ["run1", "run2", "run3"],
            "experiment_id": ["exp1", "exp1", "exp1"],
            "metric_value": [0.85, 0.87, 0.83],
            "param_value": ["value1", "value2", "value3"],
        }
    )
