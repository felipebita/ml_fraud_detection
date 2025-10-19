import subprocess
from logging import Logger
from typing import Any

import lightgbm as lgb
import mlflow
import numpy as np
import pandas as pd
import xgboost as xgb
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from src.utils.config import get_config
from src.utils.logger import LoggerContext, get_logger


class ModelWithThreshold(mlflow.pyfunc.PythonModel):
    def __init__(self, model: Pipeline, threshold: float):
        self.model = model
        self.threshold = threshold

    def predict(self, _context: Any, model_input: pd.DataFrame) -> np.ndarray:
        probabilities = self.model.predict_proba(model_input)[:, 1]
        return np.array((probabilities >= self.threshold), dtype=int)


def get_git_commit_hash() -> str | None:
    """Gets the current git commit hash."""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .strip()
            .decode("utf-8")
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


class ModelTrainer:
    """
    Trains and saves the final model.
    """

    def __init__(self, config: dict[str, Any], logger: Logger):
        self.config = config
        self.logger = logger
        self.experiment_name = self.config["final_model_train"]["experiment_name"]
        self.run_name = self.config["final_model_train"]["run_name"]
        self.best_run_metric = self.config["final_model_train"]["best_run_metric"]
        self.model_prefix = self.config["final_model_train"]["prefix"]
        self.registered_model_name = self.config["final_model_train"][
            "registered_model_name"
        ]
        self.target = self.config["model_training"]["target_variable"]
        self.features_to_drop = self.config["model_training"]["features_to_drop"] + [
            self.target
        ]

        mlflow.set_tracking_uri(self.config["mlflow"]["tracking_uri"])

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

    def _convert_param_types(self, params: dict[str, Any]) -> dict[str, Any]:
        """Converts string params to their correct types (int, float, bool)."""
        converted_params = {}
        for k, v in params.items():
            try:
                if "." in v:
                    converted_params[k] = float(v)
                else:
                    converted_params[k] = int(v)
            except (ValueError, TypeError):
                if v.lower() == "true":
                    converted_params[k] = True
                elif v.lower() == "false":
                    converted_params[k] = False
                else:
                    converted_params[k] = v
        return converted_params

    def get_params_from_mlflow(
        self,
    ) -> tuple[str, dict[str, Any], dict[str, Any], float | None, str, str]:
        """
        Fetches model parameters and metrics from an MLflow run.
        """
        with LoggerContext(
            self.logger,
            "Fetching parameters from MLflow",
            experiment_name=self.experiment_name,
            run_name=self.run_name,
        ):
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                raise ValueError(f"Experiment '{self.experiment_name}' not found.")

            if self.run_name == "BEST":
                runs = mlflow.search_runs(
                    experiment_ids=[experiment.experiment_id],
                    order_by=[f"metrics.{self.best_run_metric} DESC"],
                    max_results=1,
                )
                if not runs.empty:
                    run_id = runs.iloc[0]["run_id"]
                else:
                    raise ValueError(
                        f"No runs found in experiment '{self.experiment_name}'"
                    )
            else:
                runs = mlflow.search_runs(
                    experiment_ids=[experiment.experiment_id],
                    filter_string=f"tags.mlflow.runName = '{self.run_name}'",
                )
                if not runs.empty:
                    run_id = runs.iloc[0]["run_id"]
                else:
                    raise ValueError(
                        f"Run '{self.run_name}' not found in experiment '{self.experiment_name}'"
                    )

            run = mlflow.get_run(run_id)
            model_name = run.data.params["model_name"]
            best_run_name = run.data.tags["mlflow.runName"]
            params = {
                k: v
                for k, v in run.data.params.items()
                if k not in ["model_name", "cv_folds"]
            }
            metrics = {k: v for k, v in run.data.metrics.items() if "avg" in k}
            if "weighted_threshold" in run.data.metrics:
                threshold = run.data.metrics.get("weighted_threshold")
            else:
                threshold = run.data.metrics.get("avg_optimal_threshold")
            return (
                model_name,
                self._convert_param_types(params),
                metrics,
                threshold,
                run_id,
                best_run_name,
            )

    def train(self) -> None:
        """
        Trains the final model.
        """
        with LoggerContext(self.logger, "Starting model training"):
            (
                model_name,
                params,
                metrics,
                threshold,
                best_run_id,
                best_run_name,
            ) = self.get_params_from_mlflow()

            if threshold is None:
                self.logger.warning(
                    "No threshold found in the MLflow run. Using 0.5 as default."
                )
                threshold = 0.5

            with LoggerContext(self.logger, "Loading data"):
                df = pd.read_parquet(self.config["data"]["processed_path"])
                X = df.drop(columns=self.features_to_drop)
                y = df[self.target]
                scale_pos_weight = (y == 0).sum() / (y == 1).sum()

            with LoggerContext(
                self.logger, f"Training {model_name} with params: {params}"
            ):
                pipeline = self._get_model_pipeline(
                    model_name, params, scale_pos_weight
                )
                pipeline.fit(X, y)

            client = MlflowClient()
            final_models_experiment = client.get_experiment_by_name("final_models")
            if (
                final_models_experiment
                and final_models_experiment.lifecycle_stage == "deleted"
            ):
                client.restore_experiment(final_models_experiment.experiment_id)
                self.logger.info("Restored deleted experiment 'final_models'.")

            with LoggerContext(self.logger, "Saving model"):
                mlflow.set_experiment("final_models")

                registered_model_name = (
                    f"{self.model_prefix}_{self.registered_model_name}"
                    if self.model_prefix
                    else self.registered_model_name
                )

                run_name = f"final_{self.experiment_name}_{best_run_name}"
                with mlflow.start_run(run_name=run_name):
                    mlflow.log_params(params)
                    mlflow.log_metrics(metrics)
                    mlflow.log_metric("profit_threshold", threshold)
                    mlflow.set_tag("best_run_id", best_run_id)

                    git_commit = get_git_commit_hash()
                    if git_commit:
                        mlflow.set_tag("git_commit", git_commit)

                    model_with_threshold = ModelWithThreshold(
                        model=pipeline, threshold=threshold
                    )

                    signature = infer_signature(
                        X, model_with_threshold.predict(None, X)
                    )
                    mlflow.pyfunc.log_model(
                        "model",
                        python_model=model_with_threshold,
                        registered_model_name=registered_model_name,
                        signature=signature,
                    )

                self.logger.info(
                    f"Model trained and saved to MLflow as {registered_model_name}."
                )


if __name__ == "__main__":
    main_logger = get_logger("ModelTraining")
    config = get_config()

    trainer = ModelTrainer(config=config, logger=main_logger)
    trainer.train()
