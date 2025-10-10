from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.model.training import ModelTrainer


@pytest.fixture
def mock_config():
    """Provides a mock configuration for tests."""
    return {
        "model_training": {
            "target_variable": "isFraud",
            "features_to_drop": ["step", "nameOrig", "nameDest"],
        },
        "mlflow": {
            "tracking_uri": "sqlite:///mlflow.duckdb",
            "experiment_name": "test_experiment",
        },
        "data": {"processed_path": "dummy_path.parquet"},
    }


@pytest.fixture
def mock_logger():
    """Provides a mock logger."""
    return MagicMock()


@pytest.fixture
def sample_df():
    """Returns a sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "step": [1, 2, 3],
            "nameOrig": ["a", "b", "c"],
            "nameDest": ["d", "e", "f"],
            "isFraud": [0, 1, 0],
            "feature1": [0.1, 0.2, 0.3],
        }
    )


@patch("src.model.training.pd.read_parquet")
@patch("src.model.training.mlflow")
def test_train_with_best_run(
    mock_mlflow, mock_read_parquet, mock_config, mock_logger, sample_df
):
    """Tests the training process when selecting the BEST run."""
    # Arrange
    mock_experiment = MagicMock()
    mock_experiment.experiment_id = "123"
    mock_mlflow.get_experiment_by_name.return_value = mock_experiment

    mock_runs_df = pd.DataFrame({"run_id": ["run1"]})
    mock_mlflow.search_runs.return_value = mock_runs_df

    mock_run = MagicMock()
    mock_run.data.params = {"model_name": "randomforest", "n_estimators": "100"}
    mock_run.data.metrics = {"avg_f1": 0.95}
    mock_mlflow.get_run.return_value = mock_run

    mock_read_parquet.return_value = sample_df

    trainer = ModelTrainer(
        config=mock_config,
        logger=mock_logger,
        experiment_name="test_experiment",
        run_name="BEST",
    )

    # Act
    trainer.train()

    # Assert
    mock_mlflow.set_tracking_uri.assert_called_with("sqlite:///mlflow.duckdb")
    mock_mlflow.get_experiment_by_name.assert_called_with("test_experiment")
    mock_mlflow.search_runs.assert_called_once_with(
        experiment_ids=["123"], order_by=["metrics.avg_f1 DESC"], max_results=1
    )
    mock_mlflow.get_run.assert_called_with("run1")
    mock_read_parquet.assert_called_with("dummy_path.parquet")
    mock_mlflow.log_metrics.assert_called_with({"avg_f1": 0.95})
    assert mock_mlflow.sklearn.log_model.call_count == 1
