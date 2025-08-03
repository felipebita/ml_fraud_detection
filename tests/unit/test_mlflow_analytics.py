# tests/unit/test_mlflow_analytics.py
from unittest.mock import Mock

import pandas as pd

from src.utils.mlflow_analytics import MLflowAnalytics


class TestMLflowAnalytics:
    """Test MLflow analytics functionality."""

    def test_initialization(self):
        """Test analytics class initialization."""
        mock_conn = Mock()
        analytics = MLflowAnalytics(mock_conn)

        assert analytics.conn == mock_conn

    def test_get_model_comparison(self, sample_experiment_data):
        """Test model comparison query execution."""
        mock_conn = Mock()
        # Change from .df() to .fetchdf()
        mock_conn.execute.return_value.fetchdf.return_value = sample_experiment_data

        analytics = MLflowAnalytics(mock_conn)
        result = analytics.get_model_comparison()

        # Verify query was executed
        mock_conn.execute.assert_called_once()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_experiment_data)

    def test_get_experiment_timeline(self):
        """Test experiment timeline query."""
        mock_conn = Mock()
        expected_data = pd.DataFrame(
            {
                "hour": ["2024-01-01", "2024-01-02"],  # Changed from 'start_time'
                "runs_count": [5, 10],
                "avg_f1": [0.85, 0.87],
            }
        )
        # Change from .df() to .fetchdf()
        mock_conn.execute.return_value.fetchdf.return_value = expected_data

        analytics = MLflowAnalytics(mock_conn)
        result = analytics.get_experiment_timeline()

        # Verify correct query pattern
        assert isinstance(result, pd.DataFrame)
        assert "hour" in result.columns

    def test_find_best_hyperparameters(self):
        """Test finding best hyperparameters for a model."""
        mock_conn = Mock()
        expected_data = pd.DataFrame(
            {
                "param_name": ["learning_rate", "max_depth"],
                "param_value": ["0.1", "5"],
                "metric_value": [0.95, 0.95],
            }
        )
        # Change from .df() to .fetchdf()
        mock_conn.execute.return_value.fetchdf.return_value = expected_data

        analytics = MLflowAnalytics(mock_conn)
        # Fix parameter names: model_type and metric (not model_name and metric_name)
        result = analytics.find_best_hyperparameters(
            model_type="xgboost", metric="accuracy"
        )

        # Verify query includes model name and metric
        query_call = mock_conn.execute.call_args[0][0]
        assert "xgboost" in query_call
        assert "accuracy" in query_call
        assert len(result) == 2
