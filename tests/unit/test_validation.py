# tests/unit/test_validation.py
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.model.validation import (
    BaseExperiment,
    GridSearchExperiment,
    QuickExperiment,
)


@pytest.fixture
def mock_config():
    """Provides a mock configuration for tests."""
    return {
        "model_training": {
            "cv_folds": 5,
            "skip_folds": 1,
            "target_variable": "isFraud",
            "features_to_drop": ["feature_to_drop"],
            "exp_name_prefix": "test_prefix",
            "models_to_compare": ["randomforest", "xgboost"],
            "model_params": {
                "randomforest": {"n_estimators": 10},
                "xgboost": {"n_estimators": 20},
            },
            "model_gs": "lightgbm",
            "param_grid": {"n_estimators": [50, 100]},
            "number_of_rows": 1000,
            "run_name_prefix": "run_prefix",
        },
        "mlflow": {
            "tracking_uri": "sqlite:///test.db",
            "experiment_name": "test_experiment",
        },
        "data": {"processed_path": "/path/to/processed.parquet"},
    }


@pytest.fixture
def sample_df():
    """Returns a sample DataFrame for testing."""
    data = {
        "feature1": range(100),
        "feature2": range(100),
        "feature_to_drop": [0] * 100,
        "isFraud": ([0] * 50 + [1] * 50),
    }
    return pd.DataFrame(data)


@patch("src.model.validation.mlflow")
def test_base_experiment_init(mock_mlflow, mock_config):
    """Tests the initialization of BaseExperiment."""
    logger = MagicMock()

    class ConcreteExperiment(BaseExperiment):
        def run(self):
            pass

    exp = ConcreteExperiment(config=mock_config, logger=logger)

    mock_mlflow.set_tracking_uri.assert_called_once_with("sqlite:///test.db")
    expected_exp_name = "test_prefix_test_experiment"
    mock_mlflow.set_experiment.assert_called_once_with(expected_exp_name)
    assert exp.cv_folds == 5
    assert exp.skip_folds == 1


class TestBaseExperiment:
    @pytest.mark.parametrize(
        "model_name, expected_mock_name",
        [
            ("randomforest", "mock_rf"),
            ("xgboost", "mock_xgb"),
            ("lightgbm", "mock_lgbm"),
        ],
    )
    @patch("src.model.validation.RandomForestClassifier")
    @patch("src.model.validation.xgb.XGBClassifier")
    @patch("src.model.validation.lgb.LGBMClassifier")
    def test_get_model_pipeline(
        self, mock_lgbm, mock_xgb, mock_rf, model_name, expected_mock_name, mock_config
    ):
        """Tests that the correct model pipeline is returned."""
        logger = MagicMock()

        class ConcreteExperiment(BaseExperiment):
            def run(self):
                pass

        exp = ConcreteExperiment(config=mock_config, logger=logger)
        pipeline = exp._get_model_pipeline(model_name, {}, 1.0)

        mocks = {"mock_rf": mock_rf, "mock_xgb": mock_xgb, "mock_lgbm": mock_lgbm}
        expected_mock = mocks[expected_mock_name]

        assert pipeline.steps[0][0] == "classifier"
        expected_mock.assert_called_once()

    def test_get_model_pipeline_unsupported(self, mock_config):
        """Tests that an error is raised for an unsupported model."""
        logger = MagicMock()

        class ConcreteExperiment(BaseExperiment):
            def run(self):
                pass

        exp = ConcreteExperiment(config=mock_config, logger=logger)
        with pytest.raises(ValueError):
            exp._get_model_pipeline("unsupported_model", {}, 1.0)

    def test_calculate_metrics(self, mock_config):
        """Tests that metrics are calculated correctly."""
        logger = MagicMock()

        class ConcreteExperiment(BaseExperiment):
            def run(self):
                pass

        exp = ConcreteExperiment(config=mock_config, logger=logger)
        y_true = pd.Series([0, 1, 0, 1])
        y_pred = pd.Series([0, 1, 1, 1])
        y_pred_proba = pd.Series([0.1, 0.9, 0.6, 0.8])

        metrics = exp._calculate_metrics(y_true, y_pred, y_pred_proba)

        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert "roc_auc" in metrics
        assert "balanced_accuracy" in metrics
        assert pytest.approx(metrics["recall"]) == 1.0
        assert pytest.approx(metrics["precision"]) == 0.6666666666666666


@patch("src.model.validation.TimeSeriesSplit")
@patch("src.model.validation.pd.read_parquet")
@patch("src.model.validation.mlflow")
class TestQuickExperiment:
    def test_run(
        self,
        mock_mlflow,
        mock_read_parquet,
        mock_time_series_split,
        mock_config,
        sample_df,
    ):
        """Tests the main run method of QuickExperiment."""
        mock_read_parquet.return_value = sample_df
        mock_tscv = MagicMock()
        mock_time_series_split.return_value = mock_tscv
        logger = MagicMock()

        with patch(
            "src.model.validation.BaseExperiment._execute_cv"
        ) as mock_execute_cv:
            exp = QuickExperiment(config=mock_config, logger=logger)
            exp.run()

            assert mock_execute_cv.call_count == 2
            assert mock_mlflow.start_run.call_count == 2

            # First call (randomforest)
            args, kwargs = mock_execute_cv.call_args_list[0]
            pd.testing.assert_frame_equal(
                args[1], sample_df.drop(columns=["feature_to_drop", "isFraud"])
            )
            pd.testing.assert_series_equal(args[2], sample_df["isFraud"])
            assert args[3] == mock_tscv
            assert args[4] == "randomforest"
            assert kwargs["log_model"] is True

            # Second call (xgboost)
            args, kwargs = mock_execute_cv.call_args_list[1]
            assert args[4] == "xgboost"

    def test_run_skip_folds_warning(
        self, mock_mlflow, mock_read_parquet, mock_time_series_split, mock_config
    ):
        """Tests that a warning is logged if all folds are skipped."""
        logger = MagicMock()
        mock_config["model_training"]["skip_folds"] = 5
        exp = QuickExperiment(config=mock_config, logger=logger)
        exp.run()
        logger.warning.assert_called_once()


@patch("src.model.validation.TimeSeriesSplit")
@patch("src.model.validation.pd.read_parquet")
@patch("src.model.validation.mlflow")
class TestGridSearchExperiment:
    def test_run(
        self,
        mock_mlflow,
        mock_read_parquet,
        mock_time_series_split,
        mock_config,
        sample_df,
    ):
        """Tests the main run method of GridSearchExperiment."""
        mock_read_parquet.return_value = sample_df
        mock_tscv = MagicMock()
        mock_time_series_split.return_value = mock_tscv
        logger = MagicMock()

        with patch(
            "src.model.validation.BaseExperiment._execute_cv"
        ) as mock_execute_cv:
            exp = GridSearchExperiment(config=mock_config, logger=logger)
            exp.run()

            assert mock_execute_cv.call_count == 2  # For two param sets
            assert mock_mlflow.start_run.call_count == 2

    def test_run_skip_folds_warning(
        self, mock_mlflow, mock_read_parquet, mock_time_series_split, mock_config
    ):
        """Tests that a warning is logged if all folds are skipped."""
        logger = MagicMock()
        mock_config["model_training"]["skip_folds"] = 5
        exp = GridSearchExperiment(config=mock_config, logger=logger)
        exp.run()
        logger.warning.assert_called_once()
