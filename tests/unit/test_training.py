import subprocess
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.model.training import ModelTrainer, ModelWithThreshold, get_git_commit_hash


@pytest.fixture
def mock_config():
    """Provides a mock configuration for tests."""
    return {
        "final_model_train": {
            "experiment_name": "test_experiment",
            "run_name": "BEST",
            "best_run_metric": "avg_f1",
            "prefix": "test",
            "registered_model_name": "test_model",
        },
        "model_training": {
            "target_variable": "isFraud",
            "features_to_drop": ["step", "nameOrig", "nameDest"],
        },
        "mlflow": {"tracking_uri": "sqlite:///mlflow.duckdb"},
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


@pytest.fixture
def mock_model():
    """Pytest fixture for a mock model."""
    model = MagicMock()
    model.predict_proba.return_value = np.array(
        [[0.1, 0.9], [0.8, 0.2], [0.4, 0.6], [0.9, 0.1]]
    )
    return model


@patch("src.model.training.pd.read_parquet")
@patch("src.model.training.mlflow")
@patch("src.model.training.get_git_commit_hash", return_value="test_hash")
def test_train_with_best_run(
    mock_get_hash, mock_mlflow, mock_read_parquet, mock_config, mock_logger, sample_df
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
    mock_run.data.metrics = {"avg_f1": 0.95, "weighted_threshold": 0.6}
    mock_run.data.tags = {"mlflow.runName": "test_run_name"}
    mock_mlflow.get_run.return_value = mock_run

    mock_read_parquet.return_value = sample_df

    trainer = ModelTrainer(config=mock_config, logger=mock_logger)

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
    assert mock_mlflow.pyfunc.log_model.call_count == 1


def test_model_with_threshold(mock_model):
    """
    Tests the ModelWithThreshold class to ensure it correctly applies the threshold
    to the model's probability predictions.
    """
    # Arrange
    threshold = 0.5
    model_with_threshold = ModelWithThreshold(model=mock_model, threshold=threshold)
    expected_predictions = np.array([1, 0, 1, 0])

    # Act
    predictions = model_with_threshold.predict(None, np.array([[1, 2], [3, 4]]))

    # Assert
    np.testing.assert_array_equal(predictions, expected_predictions)
    mock_model.predict_proba.assert_called_once()


@patch("src.model.training.mlflow")
def test_train_raises_experiment_not_found(mock_mlflow, mock_config, mock_logger):
    """Tests that a ValueError is raised when the experiment is not found."""
    # Arrange
    mock_mlflow.get_experiment_by_name.return_value = None
    trainer = ModelTrainer(config=mock_config, logger=mock_logger)

    # Act & Assert
    with pytest.raises(ValueError, match="Experiment 'test_experiment' not found."):
        trainer.get_params_from_mlflow()


@patch("src.model.training.mlflow")
def test_train_raises_run_not_found(mock_mlflow, mock_config, mock_logger):
    """Tests that a ValueError is raised when the run is not found."""
    # Arrange
    mock_experiment = MagicMock()
    mock_experiment.experiment_id = "123"
    mock_mlflow.get_experiment_by_name.return_value = mock_experiment
    mock_mlflow.search_runs.return_value = pd.DataFrame()
    mock_config["final_model_train"]["run_name"] = "specific_run"
    trainer = ModelTrainer(config=mock_config, logger=mock_logger)

    # Act & Assert
    with pytest.raises(
        ValueError, match="Run 'specific_run' not found in experiment 'test_experiment'"
    ):
        trainer.get_params_from_mlflow()


def test_get_model_pipeline_raises_value_error(mock_config, mock_logger):
    """Tests that a ValueError is raised for an unsupported model."""
    # Arrange
    trainer = ModelTrainer(config=mock_config, logger=mock_logger)

    # Act & Assert
    with pytest.raises(ValueError, match="Model unsupported_model not supported."):
        trainer._get_model_pipeline("unsupported_model", {}, 1.0)


def test_convert_param_types(mock_config, mock_logger):
    """Tests the _convert_param_types method."""
    # Arrange
    trainer = ModelTrainer(config=mock_config, logger=mock_logger)
    params = {
        "int_param": "10",
        "float_param": "0.5",
        "bool_true_param": "true",
        "bool_false_param": "false",
        "string_param": "test",
    }

    # Act
    converted_params = trainer._convert_param_types(params)

    # Assert
    assert converted_params["int_param"] == 10
    assert converted_params["float_param"] == 0.5
    assert converted_params["bool_true_param"] is True
    assert converted_params["bool_false_param"] is False
    assert converted_params["string_param"] == "test"


@patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git"))
def test_get_git_commit_hash_fails(mock_subprocess):
    """Tests that get_git_commit_hash returns None when the git command fails."""
    # Act
    commit_hash = get_git_commit_hash()

    # Assert
    assert commit_hash is None


@patch("src.model.training.pd.read_parquet")
@patch("src.model.training.mlflow")
@patch("src.model.training.get_git_commit_hash", return_value="test_hash")
def test_train_with_no_threshold(
    mock_get_hash, mock_mlflow, mock_read_parquet, mock_config, mock_logger, sample_df
):
    """Tests the training process when no threshold is found in the MLflow run."""
    # Arrange
    mock_experiment = MagicMock()
    mock_experiment.experiment_id = "123"
    mock_mlflow.get_experiment_by_name.return_value = mock_experiment

    mock_runs_df = pd.DataFrame({"run_id": ["run1"]})
    mock_mlflow.search_runs.return_value = mock_runs_df

    mock_run = MagicMock()
    mock_run.data.params = {"model_name": "randomforest", "n_estimators": "100"}
    mock_run.data.metrics = {"avg_f1": 0.95}
    mock_run.data.tags = {"mlflow.runName": "test_run_name"}
    mock_mlflow.get_run.return_value = mock_run

    mock_read_parquet.return_value = sample_df

    trainer = ModelTrainer(config=mock_config, logger=mock_logger)

    # Act
    trainer.train()

    # Assert
    mock_mlflow.log_metric.assert_called_with("profit_threshold", 0.5)
