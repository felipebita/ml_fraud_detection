# tests/unit/test_mlflow_duckdb_setup.py
from unittest.mock import Mock, patch

import pytest

from src.utils.mlflow_duckdb_setup import MLflowDuckDBManager


@pytest.fixture
def test_config(tmp_path):
    """Provides a sample MLflow config dictionary for tests."""
    return {
        "tracking_uri": f"sqlite:///{tmp_path}/test.db",
        "artifact_root": str(tmp_path / "artifacts"),
        "experiment_name": "test_experiment",
    }


class TestMLflowDuckDBManager:
    """Test MLflow DuckDB manager class."""

    def test_manager_initialization(self, tmp_path):
        """Test manager initializes with config."""
        config = {
            "tracking_uri": f"sqlite:///{tmp_path}/test.db",
            "artifact_root": str(tmp_path / "artifacts"),
            "experiment_name": "test_experiment",
        }

        manager = MLflowDuckDBManager(config)

        assert manager.config == config
        assert (tmp_path / "artifacts").exists()

    @patch("mlflow.set_tracking_uri")
    @patch("mlflow.set_experiment")
    @patch("mlflow.get_experiment_by_name")
    def test_setup_mlflow_existing_experiment(
        self, mock_get_exp, mock_set_exp, mock_set_uri, test_config
    ):
        """Test MLflow setup with existing experiment."""
        # Setup
        manager = MLflowDuckDBManager(test_config)

        mock_exp = Mock()
        mock_exp.experiment_id = "123"
        mock_get_exp.return_value = mock_exp

        # Execute
        exp_id = manager.setup_mlflow()

        # Verify
        assert exp_id == "123"
        mock_set_uri.assert_called_once_with(test_config["tracking_uri"])
        mock_set_exp.assert_called_once_with(test_config["experiment_name"])

    @patch("mlflow.set_tracking_uri")
    @patch("mlflow.set_experiment")
    @patch("mlflow.get_experiment_by_name")
    @patch("mlflow.create_experiment")
    def test_setup_mlflow_new_experiment(
        self, mock_create, mock_get_exp, mock_set_exp, mock_set_uri, test_config
    ):
        """Test MLflow setup creating new experiment."""
        # Setup
        manager = MLflowDuckDBManager(test_config)

        mock_get_exp.return_value = None
        mock_create.return_value = "456"

        # Execute
        exp_id = manager.setup_mlflow()

        # Verify
        assert exp_id == "456"
        mock_create.assert_called_once()

    @patch("duckdb.connect")
    def test_get_connection(self, mock_connect, test_config):
        """Test DuckDB connection creation."""
        manager = MLflowDuckDBManager(test_config)

        # Test read-write connection
        _ = manager.get_connection(read_only=False)
        mock_connect.assert_called_with(manager.db_path, read_only=False)

        # Test read-only connection
        _ = manager.get_connection(read_only=True)
        mock_connect.assert_called_with(manager.db_path, read_only=True)

    @patch("duckdb.connect")
    def test_query_experiments(self, mock_connect, test_config):
        """Test querying experiments."""
        # Setup
        manager = MLflowDuckDBManager(test_config)

        mock_conn = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.fetchdf.return_value = []

        # Execute
        _ = manager.query_experiments("SELECT * FROM runs")

        # Verify
        mock_conn.execute.assert_called_once_with("SELECT * FROM runs")
        mock_connect.assert_called_with(manager.db_path, read_only=True)

    @patch("duckdb.connect")
    def test_connection_failure(self, mock_connect, test_config):
        """Test handling of connection failures."""
        mock_connect.side_effect = RuntimeError("Connection failed")

        manager = MLflowDuckDBManager(test_config)

        with pytest.raises(RuntimeError, match="Connection failed"):
            manager.get_connection()
