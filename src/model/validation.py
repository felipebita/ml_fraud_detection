import subprocess
from abc import ABC, abstractmethod
from logging import Logger
from typing import Any

import lightgbm as lgb
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import pandas as pd
import seaborn as sns
import xgboost as xgb
from mlflow.models.signature import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    PrecisionRecallDisplay,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import ParameterGrid, TimeSeriesSplit
from sklearn.pipeline import Pipeline

from src.model.financial_metrics import FinancialAnalyzer
from src.utils.config import get_config
from src.utils.logger import LoggerContext, get_logger


class BaseExperiment(ABC):
    """
    Abstract base class for model validation experiments.
    """

    def __init__(self, config: dict[str, Any], logger: Logger):
        self.config = config
        self.logger = logger
        self.cv_folds = self.config["model_training"]["cv_folds"]
        self.skip_folds = self.config["model_training"]["skip_folds"]
        self.target = self.config["model_training"]["target_variable"]
        self.features_to_drop = self.config["model_training"]["features_to_drop"] + [
            self.target,
            "amount",
        ]

        mlflow.set_tracking_uri(self.config["mlflow"]["tracking_uri"])
        exp_name_prefix = self.config["model_training"]["exp_name_prefix"]
        base_experiment_name = self.config["mlflow"]["experiment_name"]
        if exp_name_prefix:
            base_experiment_name = f"{exp_name_prefix}_{base_experiment_name}"

        current_experiment_name = base_experiment_name
        counter = 2
        while True:
            experiment = mlflow.get_experiment_by_name(current_experiment_name)
            if experiment is None:
                mlflow.set_experiment(current_experiment_name)
                break
            if experiment.lifecycle_stage == "active":
                mlflow.set_experiment(current_experiment_name)
                break
            if experiment.lifecycle_stage == "deleted":
                current_experiment_name = f"{base_experiment_name}_v{counter}"
                counter += 1

    def _get_model_pipeline(
        self, model_name: str, params: dict[str, Any], scale_pos_weight: float
    ) -> Pipeline:
        if model_name == "randomforest":
            model = RandomForestClassifier(**params)
        elif model_name == "xgboost":
            model = xgb.XGBClassifier(scale_pos_weight=scale_pos_weight, **params)
        elif model_name == "lightgbm":
            model = lgb.LGBMClassifier(**params)
        else:
            raise ValueError(f"Model {model_name} not supported.")
        return Pipeline(steps=[("classifier", model)])

    def _calculate_metrics(
        self, y_true: pd.Series, y_pred: pd.Series, y_pred_proba: Any
    ) -> dict[str, float]:
        return {
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "roc_auc": roc_auc_score(y_true, y_pred_proba),
            "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        }

    def _execute_cv(
        self,
        pipeline: Pipeline,
        X: pd.DataFrame,
        y: pd.Series,
        amounts: pd.Series,
        tscv: TimeSeriesSplit,
        model_name: str | None = None,
        log_model: bool = False,
    ) -> None:
        fold_metrics_storage: dict[str, list[float]] = {}
        financial_analyzer = FinancialAnalyzer()
        for fold, (train_index, val_index) in enumerate(tscv.split(X), 1):
            if fold <= self.skip_folds:
                self.logger.info(f"Skipping fold {fold}/{self.cv_folds}")
                continue
            with LoggerContext(self.logger, f"Fold {fold}/{self.cv_folds}"):
                X_train, X_val = X.iloc[train_index], X.iloc[val_index]
                y_train, y_val = y.iloc[train_index], y.iloc[val_index]
                amounts_val = amounts.iloc[val_index]

                pipeline.fit(X_train, y_train)
                y_pred_proba = pipeline.predict_proba(X_val)[:, 1]

                (
                    optimal_threshold,
                    max_profit,
                ) = financial_analyzer.find_optimal_threshold(
                    y_val.to_numpy(), y_pred_proba, amounts_val.to_numpy()
                )
                y_pred = (y_pred_proba >= optimal_threshold).astype(int)

                metrics = self._calculate_metrics(y_val, y_pred, y_pred_proba)
                metrics["optimal_threshold"] = optimal_threshold
                metrics["max_profit"] = max_profit

                mlflow.log_metrics({f"{k}_fold_{fold}": v for k, v in metrics.items()})
                for k, v in metrics.items():
                    fold_metrics_storage.setdefault(k, []).append(v)
                self.logger.info(f"Fold {fold} metrics: {metrics}")

                # Confusion Matrix
                fig_cm, ax_cm = plt.subplots(figsize=(8, 6))
                cm = confusion_matrix(y_val, y_pred)
                sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax_cm)
                ax_cm.set_title(f"Confusion Matrix - Fold {fold}")
                ax_cm.set_ylabel("Actual")
                ax_cm.set_xlabel("Predicted")
                confusion_matrix_path = f"confusion_matrix_fold_{fold}.png"
                fig_cm.savefig(confusion_matrix_path)
                plt.close(fig_cm)
                mlflow.log_artifact(confusion_matrix_path, "confusion_matrices")

                # Precision-Recall Curve
                fig_pr, ax_pr = plt.subplots(figsize=(8, 6))
                PrecisionRecallDisplay.from_estimator(pipeline, X_val, y_val, ax=ax_pr)
                ax_pr.set_title(f"Precision-Recall Curve - Fold {fold}")
                precision_recall_path = f"precision_recall_fold_{fold}.png"
                fig_pr.savefig(precision_recall_path)
                plt.close(fig_pr)
                mlflow.log_artifact(precision_recall_path, "precision_recall_curves")

        avg_metrics = {
            f"avg_{metric}": sum(values) / len(values)
            for metric, values in fold_metrics_storage.items()
        }
        std_metrics = {
            f"std_{metric}": pd.Series(values).std()
            for metric, values in fold_metrics_storage.items()
        }

        # Calculate weighted threshold
        thresholds = fold_metrics_storage.get("optimal_threshold", [])
        weights = self.config["model_training"].get("th_weights", [])
        if weights and len(weights) == len(thresholds):
            weighted_threshold = sum(
                t * w for t, w in zip(thresholds, weights, strict=False)
            ) / sum(weights)
            avg_metrics["weighted_threshold"] = weighted_threshold

        mlflow.log_metrics(avg_metrics)
        mlflow.log_metrics(std_metrics)

        if log_model:
            signature = infer_signature(X_train, y_pred)
            pip_reqs = (
                subprocess.check_output(["uv", "pip", "freeze"])
                .decode("utf-8")
                .split("\n")
            )
            mlflow.sklearn.log_model(
                sk_model=pipeline,
                artifact_path=f"{model_name}_pipeline",
                signature=signature,
                pip_requirements=pip_reqs,
            )

    @abstractmethod
    def run(self) -> None:
        """Abstract method to run the experiment."""
        pass


class QuickExperiment(BaseExperiment):
    """
    Runs a quick comparison of multiple models with fixed hyperparameters.
    """

    def __init__(self, config: dict[str, Any], logger: Logger):
        super().__init__(config, logger)
        self.models_to_compare = self.config["model_training"]["models_to_compare"]
        self.model_params = self.config["model_training"]["model_params"]

    def run(self) -> None:
        if self.skip_folds >= self.cv_folds:
            self.logger.warning(
                f"All folds were skipped because skip_folds ({self.skip_folds}) "
                f"is greater than or equal to cv_folds ({self.cv_folds})."
            )
            return
        with LoggerContext(self.logger, "Data Loading"):
            df = pd.read_parquet(self.config["data"]["processed_path"])
            number_of_rows = self.config["model_training"]["number_of_rows"]
            if number_of_rows:
                df = df.tail(number_of_rows)

        amounts = df["amount"]
        X = df.drop(columns=self.features_to_drop)
        y = df[self.target]
        scale_pos_weight = (y == 0).sum() / (y == 1).sum()
        tscv = TimeSeriesSplit(n_splits=self.cv_folds)

        for model_name in self.models_to_compare:
            run_name_prefix = self.config["model_training"]["run_name_prefix"]
            run_name = (
                f"{run_name_prefix}_{model_name}_quick_experiment"
                if run_name_prefix
                else f"{model_name}_quick_experiment"
            )
            with (
                mlflow.start_run(run_name=run_name),
                LoggerContext(self.logger, f"Training model: {model_name}"),
            ):
                params = self.model_params.get(model_name, {})
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("cv_folds", self.cv_folds)
                mlflow.log_params(params)

                pipeline = self._get_model_pipeline(
                    model_name, params, scale_pos_weight
                )
                self._execute_cv(
                    pipeline, X, y, amounts, tscv, model_name, log_model=True
                )


class GridSearchExperiment(BaseExperiment):
    """
    Performs a grid search for each model specified in the configuration.
    """

    def __init__(self, config: dict[str, Any], logger: Logger):
        super().__init__(config, logger)
        self.models_to_compare = self.config["model_training"]["models_to_compare"]
        self.param_grids = self.config["model_training"]["param_grids"]

    def run(self) -> None:
        if self.skip_folds >= self.cv_folds:
            self.logger.warning(
                f"All folds were skipped because skip_folds ({self.skip_folds}) "
                f"is greater than or equal to cv_folds ({self.cv_folds})."
            )
            return
        with LoggerContext(self.logger, "Data Loading"):
            df = pd.read_parquet(self.config["data"]["processed_path"])
            number_of_rows = self.config["model_training"]["number_of_rows"]
            if number_of_rows:
                df = df.tail(number_of_rows)

        amounts = df["amount"]
        X = df.drop(columns=self.features_to_drop)
        y = df[self.target]
        scale_pos_weight = (y == 0).sum() / (y == 1).sum()
        tscv = TimeSeriesSplit(n_splits=self.cv_folds)

        for model_name in self.models_to_compare:
            with LoggerContext(self.logger, f"Running GridSearch for {model_name}"):
                model_param_grid = self.param_grids.get(model_name, {})
                if not model_param_grid:
                    self.logger.warning(
                        f"No param_grid found for model {model_name}. Skipping."
                    )
                    continue

                # Get the model's valid parameters
                temp_pipeline = self._get_model_pipeline(
                    model_name, {}, scale_pos_weight
                )
                model_params = (
                    temp_pipeline.get_params()["classifier"].get_params().keys()
                )

                # Filter the param_grid from config
                filtered_grid = {
                    k: v for k, v in model_param_grid.items() if k in model_params
                }
                param_grid = ParameterGrid(filtered_grid)

                for i, params in enumerate(param_grid):
                    run_name_prefix = self.config["model_training"]["run_name_prefix"]
                    run_name = (
                        f"{run_name_prefix}_{model_name}_grid_search_{i}"
                        if run_name_prefix
                        else f"{model_name}_grid_search_{i}"
                    )
                    with (
                        mlflow.start_run(run_name=run_name, nested=True),
                        LoggerContext(
                            self.logger,
                            f"Running GridSearch for {model_name} with {params}",
                        ),
                    ):
                        mlflow.log_param("model_name", model_name)
                        mlflow.log_params(params)

                        pipeline = self._get_model_pipeline(
                            model_name, params, scale_pos_weight
                        )
                        self._execute_cv(pipeline, X, y, amounts, tscv)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment",
        type=str,
        default="quick",
        choices=["quick", "grid"],
        help="Type of experiment to run",
    )
    args = parser.parse_args()

    main_logger = get_logger("ModelValidation")
    config_data = get_config()

    experiment: BaseExperiment
    if args.experiment == "quick":
        experiment = QuickExperiment(config=config_data, logger=main_logger)
    else:
        experiment = GridSearchExperiment(config=config_data, logger=main_logger)
    experiment.run()
