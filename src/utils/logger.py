import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pandas as pd
import structlog
from structlog.stdlib import LoggerFactory
from structlog.types import BoundLogger


def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = "logs/fraud_detection.log",
    json_logs: bool = False,
    environment: str = "development",
) -> None:
    """Configure structured logging for the fraud detection project"""

    # Create logs directory if needed
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure processors based on environment
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[structlog.types.Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ),
    ]

    if json_logs or environment == "production":
        # JSON output for production/analysis
        processors = shared_processors + [structlog.processors.JSONRenderer()]
    else:
        # Human-readable output for development
        processors = shared_processors + [structlog.dev.ConsoleRenderer(colors=False)]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Setup standard logging
    log_level_value = getattr(logging, log_level.upper())

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_value)

    # Configure root logger
    logging.basicConfig(
        format="%(message)s",
        handlers=[console_handler],
        level=log_level_value,
    )

    # File handler if specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5  # 10MB
        )
        file_handler.setLevel(log_level_value)
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> BoundLogger:
    """Get a structured logger instance"""
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
