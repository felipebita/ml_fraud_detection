import argparse
from logging import Logger
from typing import Any

import lightgbm as lgb
import mlflow
import pandas as pd
import xgboost as xgb
from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from src.utils.config import get_config
from src.utils.logger import LoggerContext, get_logger


class ModelTrainer:
    """
    Trains and saves the final model.
    """

    def __init__(
        self,
        config: dict[str, Any],
        logger: Logger,
        experiment_name: str,
        run_name: str,
    ):
        self.config = config
        self.logger = logger
        self.experiment_name = experiment_name
        self.run_name = run_name
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

    def get_params_from_mlflow(self) -> tuple[str, dict[str, Any], dict[str, Any]]:
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
                    order_by=["metrics.avg_f1 DESC"],
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
            params = {
                k: v
                for k, v in run.data.params.items()
                if k not in ["model_name", "cv_folds"]
            }
            metrics = {k: v for k, v in run.data.metrics.items() if "avg" in k}
            return model_name, self._convert_param_types(params), metrics

    def train(self) -> None:
        """
        Trains the final model.
        """
        with LoggerContext(self.logger, "Starting model training"):
            model_name, params, metrics = self.get_params_from_mlflow()

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

            with LoggerContext(self.logger, "Saving model"):
                mlflow.set_experiment("final_models")
                with mlflow.start_run(run_name=f"final_{model_name}"):
                    mlflow.log_params(params)
                    mlflow.log_metrics(metrics)
                    signature = infer_signature(X, pipeline.predict(X))
                    mlflow.sklearn.log_model(
                        pipeline,
                        "model",
                        registered_model_name=self.config["mlflow"]["experiment_name"],
                        signature=signature,
                    )

                self.logger.info("Model trained and saved to MLflow.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a model.")
    parser.add_argument(
        "--experiment_name",
        type=str,
        required=True,
        help="Name of the MLflow experiment.",
    )
    parser.add_argument(
        "--run_name",
        type=str,
        required=True,
        help="Name of the MLflow run or 'BEST'.",
    )
    args = parser.parse_args()

    main_logger = get_logger("ModelTraining")
    config = get_config()

    trainer = ModelTrainer(
        config=config,
        logger=main_logger,
        experiment_name=args.experiment_name,
        run_name=args.run_name,
    )
    trainer.train()
