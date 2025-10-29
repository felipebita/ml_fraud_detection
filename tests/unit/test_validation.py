# tests/unit/test_validation.py
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.data.data_processing import DataProcessor
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
            "cv_folds": 2,
            "skip_folds": 0,
            "target_variable": "isFraud",
            "features_to_drop": ["feature_to_drop"],
            "exp_name_prefix": "test_prefix",
            "models_to_compare": ["randomforest", "xgboost"],
            "model_params": {
                "randomforest": {"n_estimators": 10},
                "xgboost": {"n_estimators": 20},
            },
            "param_grids": {
                "randomforest": {"n_estimators": [50, 100]},
                "xgboost": {"max_depth": [3, 5]},
            },
            "number_of_rows": 100,
            "run_name_prefix": "run_prefix",
            "th_weights": [0.4, 0.6],
        },
        "mlflow": {
            "tracking_uri": "sqlite:///test.db",
            "experiment_name": "test_experiment",
        },
        "data": {"processed_path": "/path/to/processed.parquet"},
    }


@pytest.fixture
def sample_df():
    """
    Returns a sample DataFrame for testing, with integer columns converted to float
    to avoid MLflow schema warnings.
    """
    data = {
        "feature1": range(100),
        "feature2": range(100),
        "feature_to_drop": [0] * 100,
        "isFraud": ([0, 1] * 50),
        "amount": [10] * 100,
    }
    df = pd.DataFrame(data)
    processor = DataProcessor()
    return processor.convert_int_to_float(df)


@pytest.fixture
def mock_financial_analyzer():
    """Provides a mock FinancialAnalyzer."""
    analyzer = MagicMock()
    analyzer.find_optimal_threshold.return_value = (0.5, 1000)
    return analyzer


@patch("src.model.validation.mlflow")
def test_base_experiment_init_no_existing_experiment(mock_mlflow, mock_config):
    """Tests initialization when the experiment does not exist."""
    logger = MagicMock()
    mock_mlflow.get_experiment_by_name.return_value = None

    class ConcreteExperiment(BaseExperiment):
        def run(self):
            pass

    exp = ConcreteExperiment(config=mock_config, logger=logger)

    mock_mlflow.set_tracking_uri.assert_called_once_with("sqlite:///test.db")
    expected_exp_name = "test_prefix_test_experiment"
    mock_mlflow.get_experiment_by_name.assert_called_once_with(expected_exp_name)
    mock_mlflow.set_experiment.assert_called_once_with(expected_exp_name)
    assert exp.cv_folds == 2
    assert exp.skip_folds == 0


@patch("src.model.validation.mlflow")
def test_base_experiment_init_active_experiment_exists(mock_mlflow, mock_config):
    """Tests initialization when an active experiment with the same name exists."""
    logger = MagicMock()
    mock_experiment = MagicMock()
    mock_experiment.lifecycle_stage = "active"
    mock_mlflow.get_experiment_by_name.return_value = mock_experiment

    class ConcreteExperiment(BaseExperiment):
        def run(self):
            pass

    exp = ConcreteExperiment(config=mock_config, logger=logger)

    mock_mlflow.set_tracking_uri.assert_called_once_with("sqlite:///test.db")
    expected_exp_name = "test_prefix_test_experiment"
    mock_mlflow.get_experiment_by_name.assert_called_once_with(expected_exp_name)
    mock_mlflow.set_experiment.assert_called_once_with(expected_exp_name)
    assert exp.cv_folds == 2
    assert exp.skip_folds == 0


@patch("src.model.validation.mlflow")
def test_base_experiment_init_deleted_experiment_exists(mock_mlflow, mock_config):
    """Tests initialization when a deleted experiment with the same name exists."""
    logger = MagicMock()
    mock_deleted_experiment = MagicMock()
    mock_deleted_experiment.lifecycle_stage = "deleted"
    # The second call should return None to exit the loop
    mock_mlflow.get_experiment_by_name.side_effect = [mock_deleted_experiment, None]

    class ConcreteExperiment(BaseExperiment):
        def run(self):
            pass

    exp = ConcreteExperiment(config=mock_config, logger=logger)

    mock_mlflow.set_tracking_uri.assert_called_once_with("sqlite:///test.db")

    # Check that get_experiment_by_name was called twice
    assert mock_mlflow.get_experiment_by_name.call_count == 2

    # Check the experiment names passed to get_experiment_by_name
    original_name = "test_prefix_test_experiment"
    new_name = "test_prefix_test_experiment_v2"
    mock_mlflow.get_experiment_by_name.assert_any_call(original_name)
    mock_mlflow.get_experiment_by_name.assert_any_call(new_name)

    # Check that set_experiment was called with the new name
    mock_mlflow.set_experiment.assert_called_once_with(new_name)
    assert exp.cv_folds == 2
    assert exp.skip_folds == 0


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
    @patch("src.model.validation.mlflow")
    def test_get_model_pipeline(
        self,
        mock_mlflow,
        mock_lgbm,
        mock_xgb,
        mock_rf,
        model_name,
        expected_mock_name,
        mock_config,
    ):
        """Tests that the correct model pipeline is returned."""
        logger = MagicMock()
        mock_mlflow.get_experiment_by_name.return_value = None

        class ConcreteExperiment(BaseExperiment):
            def run(self):
                pass

        exp = ConcreteExperiment(config=mock_config, logger=logger)
        pipeline = exp._get_model_pipeline(model_name, {}, 1.0)

        mocks = {"mock_rf": mock_rf, "mock_xgb": mock_xgb, "mock_lgbm": mock_lgbm}
        expected_mock = mocks[expected_mock_name]

        assert pipeline.steps[0][0] == "classifier"
        expected_mock.assert_called_once()

    @patch("src.model.validation.mlflow")
    def test_get_model_pipeline_unsupported(self, mock_mlflow, mock_config):
        """Tests that an error is raised for an unsupported model."""
        logger = MagicMock()
        mock_mlflow.get_experiment_by_name.return_value = None

        class ConcreteExperiment(BaseExperiment):
            def run(self):
                pass

        exp = ConcreteExperiment(config=mock_config, logger=logger)
        with pytest.raises(ValueError):
            exp._get_model_pipeline("unsupported_model", {}, 1.0)

    @patch("src.model.validation.mlflow")
    def test_calculate_metrics(self, mock_mlflow, mock_config):
        """Tests that metrics are calculated correctly."""
        logger = MagicMock()
        mock_mlflow.get_experiment_by_name.return_value = None

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

    @patch("src.model.validation.plt.subplots")
    @patch("src.model.validation.sns.heatmap")
    @patch("src.model.validation.PrecisionRecallDisplay.from_estimator")
    @patch("src.model.validation.mlflow")
    @patch("src.model.validation.FinancialAnalyzer")
    def test_execute_cv(
        self,
        mock_financial_analyzer_class,
        mock_mlflow,
        mock_pr_display,
        mock_heatmap,
        mock_subplots,
        mock_config,
        sample_df,
        mock_financial_analyzer,
    ):
        """Tests the _execute_cv method."""
        logger = MagicMock()
        mock_financial_analyzer_class.return_value = mock_financial_analyzer
        mock_mlflow.get_experiment_by_name.return_value = None

        # Configure the mock for plt.subplots
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        class ConcreteExperiment(BaseExperiment):
            def run(self):
                pass

        exp = ConcreteExperiment(config=mock_config, logger=logger)
        pipeline = MagicMock()

        def predict_proba_side_effect(X):
            n_samples = len(X)
            return np.array([[0.1, 0.9]] * n_samples)

        pipeline.predict_proba.side_effect = predict_proba_side_effect
        X = sample_df.drop(columns=["feature_to_drop", "isFraud", "amount"])
        y = sample_df["isFraud"]
        amounts = sample_df["amount"]
        tscv = MagicMock()
        tscv.split.return_value = [
            (range(25), range(25, 50)),
            (range(50), range(50, 100)),
        ]

        exp._execute_cv(pipeline, X, y, amounts, tscv, "test_model", log_model=True)

        # Check financial analyzer call
        assert mock_financial_analyzer.find_optimal_threshold.call_count == 2

        # Check mlflow logging
        assert (
            mock_mlflow.log_metrics.call_count == 4
        )  # once per fold (x2), once for avg, once for std
        assert "avg_max_profit" in mock_mlflow.log_metrics.call_args_list[2].args[0]
        assert "weighted_threshold" in mock_mlflow.log_metrics.call_args_list[2].args[0]

        # Check artifact logging
        assert mock_mlflow.log_artifact.call_count == 4  # two per fold

        # Check model logging
        assert mock_mlflow.sklearn.log_model.call_count == 1


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
        mock_mlflow.get_experiment_by_name.return_value = None

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
                args[1],
                sample_df.drop(columns=["feature_to_drop", "isFraud", "amount"]),
            )
            pd.testing.assert_series_equal(args[2], sample_df["isFraud"])
            pd.testing.assert_series_equal(args[3], sample_df["amount"])
            assert args[4] == mock_tscv
            assert args[5] == "randomforest"
            assert kwargs["log_model"] is True

            # Second call (xgboost)
            args, kwargs = mock_execute_cv.call_args_list[1]
            assert args[5] == "xgboost"

    def test_run_skip_folds_warning(
        self, mock_mlflow, mock_read_parquet, mock_time_series_split, mock_config
    ):
        """Tests that a warning is logged if all folds are skipped."""
        logger = MagicMock()
        mock_config["model_training"]["skip_folds"] = 5
        mock_mlflow.get_experiment_by_name.return_value = None
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
        mock_mlflow.get_experiment_by_name.return_value = None

        with (
            patch(
                "src.model.validation.BaseExperiment._get_model_pipeline"
            ) as mock_get_pipeline,
            patch("src.model.validation.BaseExperiment._execute_cv") as mock_execute_cv,
        ):

            def get_pipeline_side_effect(model_name, params, scale_pos_weight):
                mock_model = MagicMock()
                if model_name == "randomforest":
                    mock_model.get_params.return_value = {"n_estimators": 10}
                elif model_name == "xgboost":
                    mock_model.get_params.return_value = {"max_depth": 3}

                mock_pipeline = MagicMock()
                mock_pipeline.get_params.return_value = {"classifier": mock_model}
                return mock_pipeline

            mock_get_pipeline.side_effect = get_pipeline_side_effect

            exp = GridSearchExperiment(config=mock_config, logger=logger)
            exp.run()

            # randomforest has 2 param sets, xgboost has 2
            assert mock_execute_cv.call_count == 4
            assert mock_mlflow.start_run.call_count == 4

    def test_run_skip_folds_warning(
        self, mock_mlflow, mock_read_parquet, mock_time_series_split, mock_config
    ):
        """Tests that a warning is logged if all folds are skipped."""
        logger = MagicMock()
        mock_config["model_training"]["skip_folds"] = 5
        mock_mlflow.get_experiment_by_name.return_value = None
        exp = GridSearchExperiment(config=mock_config, logger=logger)
        exp.run()
        logger.warning.assert_called_once()
