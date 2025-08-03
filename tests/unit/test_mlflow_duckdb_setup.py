# tests/unit/test_mlflow_duckdb_setup.py
from unittest.mock import Mock, patch

import pytest

from src.utils.mlflow_duckdb_setup import MLflowConfig, MLflowDuckDBManager


class TestMLflowConfig:
    """Test MLflow configuration dataclass."""

    def test_config_initialization(self):
        """Test config initializes with correct attributes."""
        config = MLflowConfig(
            tracking_uri="duckdb:///test.db",
            artifact_root="./test_artifacts",
            experiment_name="test_experiment",
        )

        assert config.tracking_uri == "duckdb:///test.db"
        assert config.artifact_root == "./test_artifacts"
        assert config.experiment_name == "test_experiment"
        assert config.db_path == "test.db"

    def test_config_defaults(self):
        """Test config with default values."""
        config = MLflowConfig()

        assert config.tracking_uri == "duckdb:///mlflow.duckdb"
        assert config.artifact_root == "./mlruns"
        assert config.experiment_name == "fraud_detection"

    @patch.dict(
        "os.environ",
        {
            "MLFLOW_TRACKING_URI": "duckdb:///env_test.db",
            "MLFLOW_ARTIFACT_ROOT": "./env_artifacts",
            "MLFLOW_EXPERIMENT_NAME": "env_experiment",
        },
    )
    def test_config_from_env(self):
        """Test config creation from environment variables."""
        config = MLflowConfig.from_env()

        assert config.tracking_uri == "duckdb:///env_test.db"
        assert config.artifact_root == "./env_artifacts"
        assert config.experiment_name == "env_experiment"


class TestMLflowDuckDBManager:
    """Test MLflow DuckDB manager class."""

    def test_manager_initialization(self, tmp_path):
        """Test manager initializes with config."""
        config = MLflowConfig(
            tracking_uri=f"duckdb:///{tmp_path}/test.db",
            artifact_root=str(tmp_path / "artifacts"),
            experiment_name="test_experiment",
        )

        manager = MLflowDuckDBManager(config)

        assert manager.config == config
        assert (tmp_path / "artifacts").exists()

    @patch("mlflow.set_tracking_uri")
    @patch("mlflow.set_experiment")
    @patch("mlflow.get_experiment_by_name")
    def test_setup_mlflow_existing_experiment(
        self, mock_get_exp, mock_set_exp, mock_set_uri
    ):
        """Test MLflow setup with existing experiment."""
        # Setup
        config = MLflowConfig()
        manager = MLflowDuckDBManager(config)

        mock_exp = Mock()
        mock_exp.experiment_id = "123"
        mock_get_exp.return_value = mock_exp

        # Execute
        exp_id = manager.setup_mlflow()

        # Verify
        assert exp_id == "123"
        mock_set_uri.assert_called_once_with(config.tracking_uri)
        mock_set_exp.assert_called_once_with(config.experiment_name)

    @patch("mlflow.set_tracking_uri")
    @patch("mlflow.set_experiment")
    @patch("mlflow.get_experiment_by_name")
    @patch("mlflow.create_experiment")
    def test_setup_mlflow_new_experiment(
        self, mock_create, mock_get_exp, mock_set_exp, mock_set_uri
    ):
        """Test MLflow setup creating new experiment."""
        # Setup
        config = MLflowConfig()
        manager = MLflowDuckDBManager(config)

        mock_get_exp.return_value = None
        mock_create.return_value = "456"

        # Execute
        exp_id = manager.setup_mlflow()

        # Verify
        assert exp_id == "456"
        mock_create.assert_called_once()

    @patch("duckdb.connect")
    def test_get_connection(self, mock_connect):
        """Test DuckDB connection creation."""
        config = MLflowConfig()
        manager = MLflowDuckDBManager(config)

        # Test read-write connection
        _ = manager.get_connection(read_only=False)
        mock_connect.assert_called_with(config.db_path, read_only=False)

        # Test read-only connection
        _ = manager.get_connection(read_only=True)
        mock_connect.assert_called_with(config.db_path, read_only=True)

    @patch("duckdb.connect")
    def test_query_experiments(self, mock_connect):
        """Test querying experiments."""
        # Setup
        config = MLflowConfig()
        manager = MLflowDuckDBManager(config)

        mock_conn = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.fetchdf.return_value = []

        # Execute
        _ = manager.query_experiments("SELECT * FROM runs")

        # Verify
        mock_conn.execute.assert_called_once_with("SELECT * FROM runs")
        mock_connect.assert_called_with(config.db_path, read_only=True)

    @patch("duckdb.connect")
    def test_connection_failure(self, mock_connect):
        """Test handling of connection failures."""
        mock_connect.side_effect = RuntimeError("Connection failed")

        config = MLflowConfig()
        manager = MLflowDuckDBManager(config)

        with pytest.raises(RuntimeError, match="Connection failed"):
            manager.get_connection()
