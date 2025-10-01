from logging import Logger
from typing import Any

import lightgbm as lgb
import mlflow
import mlflow.sklearn
import pandas as pd
import xgboost as xgb
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

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
        self, model_name: str, categorical_features: list[str]
    ) -> Pipeline:
        """
        Creates a scikit-learn pipeline with a preprocessor and a model.

        Args:
            model_name (str): The name of the model to use.
            categorical_features (List[str]): The list of categorical features.

        Returns:
            Pipeline: The scikit-learn pipeline.
        """
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
            ],
            remainder="passthrough",
        )

        if model_name == "randomforest":
            model = RandomForestClassifier(random_state=42)
        elif model_name == "xgboost":
            model = xgb.XGBClassifier(random_state=42)
        elif model_name == "lightgbm":
            model = lgb.LGBMClassifier(random_state=42)
        else:
            raise ValueError(f"Model {model_name} not supported.")

        return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", model)])

    def train_and_validate(self) -> None:
        """
        Trains and validates machine learning models and logs experiments to MLflow.
        """
        with LoggerContext(self.logger, "Data Loading"):
            train_df = pd.read_parquet(self.config["data"]["train_dataset_path"])

        TARGET = "isFraud"
        features_to_drop = [TARGET, "step", "nameOrig", "nameDest"]
        categorical_features = [
            col
            for col in train_df.select_dtypes(include=["object"]).columns
            if col not in features_to_drop
        ]

        X = train_df.drop(columns=features_to_drop)
        y = train_df[TARGET]

        tscv = TimeSeriesSplit(n_splits=self.config["model_training"]["cv_folds"])

        for model_name in self.config["model_training"]["models_to_compare"]:
            with (
                mlflow.start_run(run_name=f"{model_name}_cross_validation"),
                LoggerContext(self.logger, f"Training model: {model_name}"),
            ):
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("cv_folds", self.config["model_training"]["cv_folds"])

                pipeline = self.get_model_pipeline(model_name, categorical_features)

                for fold, (train_index, val_index) in enumerate(tscv.split(X), 1):
                    with LoggerContext(
                        self.logger,
                        f"Fold {fold}/{self.config['model_training']['cv_folds']}",
                    ):
                        X_train, X_val = X.iloc[train_index], X.iloc[val_index]
                        y_train, y_val = y.iloc[train_index], y.iloc[val_index]

                        pipeline.fit(X_train, y_train)
                        y_pred = pipeline.predict(X_val)
                        y_pred_proba = pipeline.predict_proba(X_val)[:, 1]

                        precision = precision_score(y_val, y_pred)
                        recall = recall_score(y_val, y_pred)
                        f1 = f1_score(y_val, y_pred)
                        roc_auc = roc_auc_score(y_val, y_pred_proba)

                        metrics = {
                            f"precision_fold_{fold}": precision,
                            f"recall_fold_{fold}": recall,
                            f"f1_fold_{fold}": f1,
                            f"roc_auc_fold_{fold}": roc_auc,
                        }
                        mlflow.log_metrics(metrics)
                        self.logger.info(f"Fold {fold} metrics: {metrics}")

                mlflow.sklearn.log_model(pipeline, f"{model_name}_pipeline")
                self.logger.info(
                    f"Finished training and validation for model: {model_name}"
                )


if __name__ == "__main__":
    main_logger = get_logger("ModelTraining")
    config_data = get_config()
    trainer = ModelTrainer(config=config_data, logger=main_logger)
    trainer.train_and_validate()
