import subprocess
from logging import Logger
from typing import Any

import lightgbm as lgb
import mlflow
import mlflow.sklearn
import pandas as pd
import xgboost as xgb
from mlflow.models.signature import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline

from src.utils.config import get_config
from src.utils.logger import LoggerContext, get_logger


class ModelTrainer:
    """
    A class to train and validate machine learning models.
    """

    def __init__(self, config: dict[str, Any], logger: Logger):
        """
        Initializes the ModelTrainer.

        Args:
            config (Dict[str, Any]): The project configuration.
            logger (Logger): The logger instance.
        """
        self.config = config
        self.logger = logger
        mlflow.set_tracking_uri(self.config["mlflow"]["tracking_uri"])
        mlflow.set_experiment(self.config["mlflow"]["experiment_name"])

    def get_model_pipeline(
        self,
        model_name: str,
        model_params: dict[str, Any],
        scale_pos_weight: float | None = None,
    ) -> Pipeline:
        """
        Creates a scikit-learn pipeline with a preprocessor and a model.

        Args:
            model_name (str): The name of the model to use.
            model_params (dict[str, Any]): The parameters for the model.
            scale_pos_weight (float, optional): The scale_pos_weight for XGBoost. Defaults to None.

        Returns:
            Pipeline: The scikit-learn pipeline.
        """
        if model_name == "randomforest":
            model = RandomForestClassifier(**model_params)
        elif model_name == "xgboost":
            model = xgb.XGBClassifier(scale_pos_weight=scale_pos_weight, **model_params)
        elif model_name == "lightgbm":
            model = lgb.LGBMClassifier(**model_params)
        else:
            raise ValueError(f"Model {model_name} not supported.")

        return Pipeline(steps=[("classifier", model)])

    def train_and_validate(self) -> None:
        """
        Trains and validates machine learning models and logs experiments to MLflow.
        """
        with LoggerContext(self.logger, "Data Loading"):
            train_df = pd.read_parquet(self.config["data"]["train_dataset_path"])

        TARGET = self.config["model_training"]["target_variable"]
        features_to_drop = self.config["model_training"]["features_to_drop"] + [TARGET]

        X = train_df.drop(columns=features_to_drop)
        y = train_df[TARGET]

        scale_pos_weight = (y == 0).sum() / (y == 1).sum()

        tscv = TimeSeriesSplit(n_splits=self.config["model_training"]["cv_folds"])

        for model_name in self.config["model_training"]["models_to_compare"]:
            exp_name_prefix = self.config["model_training"].get("exp_name_prefix", "")
            run_name = (
                f"{exp_name_prefix}_{model_name}_cross_validation"
                if exp_name_prefix
                else f"{model_name}_cross_validation"
            )
            with (
                mlflow.start_run(run_name=run_name),
                LoggerContext(self.logger, f"Training model: {model_name}"),
            ):
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("cv_folds", self.config["model_training"]["cv_folds"])

                model_params = self.config["model_training"]["model_params"].get(
                    model_name, {}
                )
                mlflow.log_params(model_params)

                pipeline = self.get_model_pipeline(
                    model_name, model_params, scale_pos_weight
                )

                fold_metrics_storage = {}
                for fold, (train_index, val_index) in enumerate(tscv.split(X), 1):
                    with LoggerContext(
                        self.logger,
                        f"Fold {fold}/{self.config['model_training']['cv_folds']}",
                    ):
                        X_train, X_val = X.iloc[train_index], X.iloc[val_index]
                        y_train, y_val = y.iloc[train_index], y.iloc[val_index]

                        # Log class distribution for each fold
                        train_dist = y_train.value_counts(normalize=True).to_dict()
                        val_dist = y_val.value_counts(normalize=True).to_dict()
                        mlflow.log_metrics(
                            {
                                f"train_fraud_ratio_fold_{fold}": train_dist.get(1, 0),
                                f"val_fraud_ratio_fold_{fold}": val_dist.get(1, 0),
                            }
                        )

                        pipeline.fit(X_train, y_train)
                        y_pred = pipeline.predict(X_val)
                        y_pred_proba = pipeline.predict_proba(X_val)[:, 1]

                        precision = precision_score(y_val, y_pred)
                        recall = recall_score(y_val, y_pred)
                        f1 = f1_score(y_val, y_pred)
                        roc_auc = roc_auc_score(y_val, y_pred_proba)
                        balanced_accuracy = balanced_accuracy_score(y_val, y_pred)

                        metrics = {
                            f"precision_fold_{fold}": precision,
                            f"recall_fold_{fold}": recall,
                            f"f1_fold_{fold}": f1,
                            f"roc_auc_fold_{fold}": roc_auc,
                            f"balanced_accuracy_fold_{fold}": balanced_accuracy,
                        }
                        mlflow.log_metrics(metrics)
                        fold_metrics_storage.update(metrics)
                        self.logger.info(f"Fold {fold} metrics: {metrics}")

                signature = infer_signature(X_train, y_pred)
                pip_requirements = (
                    subprocess.check_output(["uv", "pip", "freeze"])
                    .decode("utf-8")
                    .split("\n")
                )
                # Calculate average metrics across folds
                avg_metrics = {}
                for metric in [
                    "precision",
                    "recall",
                    "f1",
                    "roc_auc",
                    "balanced_accuracy",
                ]:
                    fold_values = [
                        fold_metrics_storage[f"{metric}_fold_{i}"]
                        for i in range(1, self.config["model_training"]["cv_folds"] + 1)
                    ]
                    avg_metrics[f"avg_{metric}"] = sum(fold_values) / len(fold_values)
                    avg_metrics[f"std_{metric}"] = pd.Series(fold_values).std()
                mlflow.log_metrics(avg_metrics)

                mlflow.sklearn.log_model(
                    sk_model=pipeline,
                    artifact_path=f"{model_name}_pipeline",
                    signature=signature,
                    pip_requirements=pip_requirements,
                )
                self.logger.info(
                    f"Finished training and validation for model: {model_name}"
                )


if __name__ == "__main__":
    main_logger = get_logger("ModelTraining")
    config_data = get_config()
    trainer = ModelTrainer(config=config_data, logger=main_logger)
    trainer.train_and_validate()
