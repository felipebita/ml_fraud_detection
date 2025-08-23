from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pandas as pd
import structlog
from structlog import BoundLogger

from src.utils.config import get_config


def setup_logging() -> None:
    """Configure logging for the project using the centralized configuration."""
    config = get_config()

    # The get_config function already calls logging.config.dictConfig
    # so we just need to ensure the log directory exists.
    log_config = config.get("logging_config")
    if log_config and "file" in log_config.get("handlers", {}):
        log_file = log_config["handlers"]["file"].get("filename")
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> BoundLogger:
    """Get a structured logger instance."""
    return cast(BoundLogger, structlog.get_logger(name))


class LoggerContext:
    """Context manager for operation logging"""

    def __init__(self, logger: BoundLogger, operation: str, **kwargs: Any) -> None:
        self.logger = logger
        self.operation = operation
        self.context = kwargs
        self.start_time: datetime | None = None

    def __enter__(self) -> "LoggerContext":
        self.start_time = datetime.now()
        self.logger.info(f"{self.operation}_started", **self.context)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        if self.start_time is None:
            return

        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.info(
                f"{self.operation}_completed",
                duration_seconds=duration,
                **self.context,
            )
        else:
            self.logger.error(
                f"{self.operation}_failed",
                duration_seconds=duration,
                error=str(exc_val),
                error_type=exc_type.__name__,
                **self.context,
            )


# Fraud detection specific logging utilities
def log_data_info(
    logger: BoundLogger, df: pd.DataFrame, dataset_name: str = "dataset"
) -> None:
    """Log dataset information relevant for fraud detection"""
    logger.info(
        "data_info",
        dataset=dataset_name,
        shape=df.shape,
        columns=list(df.columns),
        memory_usage_mb=df.memory_usage(deep=True).sum() / 1024**2,
        fraud_ratio=df["is_fraud"].mean() if "is_fraud" in df else None,
        missing_values=df.isnull().sum().to_dict(),
    )


def log_model_metrics(
    logger: BoundLogger, metrics: dict[str, float], model_name: str
) -> None:
    """Log model performance metrics"""
    logger.info("model_metrics", model=model_name, **metrics)


def log_prediction(logger: BoundLogger, prediction_info: dict[str, Any]) -> None:
    """Log prediction details for an audit trail"""
    logger.info("prediction_made", **prediction_info)
