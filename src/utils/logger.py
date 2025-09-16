import logging
import logging.config
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pandas as pd
import structlog
from structlog import BoundLogger

from src.utils.config import get_config


def setup_logging() -> None:  # pragma: no cover
    """Configure logging for the project using structlog and standard logging."""

    config = get_config()
    log_config = config.get("logging_config", {})
    log_level = log_config.get("root", {}).get("level", "INFO").upper()

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.render_to_log_kwargs],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Define formatters for standard logging
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True),
        foreign_pre_chain=shared_processors,
    )

    json_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Clear existing handlers
    if "pytest" not in sys.modules:
        root_logger.handlers.clear()

    else:
        # When running tests, add a handler for pytest.log
        pytest_handler = logging.FileHandler("logs/pytest.log")
        pytest_handler.setLevel(logging.DEBUG)
        pytest_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        root_logger.addHandler(pytest_handler)
        # Override propagate for all loggers during tests
        for logger_name in log_config.get("loggers", {}):
            logging.getLogger(logger_name).propagate = True

    # Create and add handlers from config
    for handler_config in log_config.get("handlers", {}).values():
        handler_level = handler_config.get("level", log_level)

        if handler_config["class"] == "logging.StreamHandler":
            handler: logging.Handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(console_formatter)
        elif handler_config["class"] == "logging.handlers.RotatingFileHandler":
            filename = Path(handler_config["filename"])
            filename.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.handlers.RotatingFileHandler(
                filename=filename,
                maxBytes=handler_config.get("maxBytes", 10485760),
                backupCount=handler_config.get("backupCount", 5),
                encoding=handler_config.get("encoding", "utf8"),
            )
            # Use the appropriate formatter from the config
            if handler_config.get("formatter") == "json":
                handler.setFormatter(json_formatter)
            else:  # Default to console for other file handlers if specified
                handler.setFormatter(console_formatter)
        else:
            continue

        handler.setLevel(handler_level)
        root_logger.addHandler(handler)

    # Configure other loggers from config
    for logger_name, logger_config in log_config.get("loggers", {}).items():
        logger = logging.getLogger(logger_name)
        logger.propagate = logger_config.get("propagate", False)
        logger.setLevel(logger_config.get("level", log_level))
        # Note: Handlers for specific loggers are not being added here
        # as they will inherit from the root logger. If specific handlers
        # are needed, that logic would be added here.
    # At the very end of setup_logging(), add:

    if "pytest" in sys.modules:
        print(f"AFTER setup: Root logger has {len(root_logger.handlers)} handlers")
        for i, handler in enumerate(root_logger.handlers):
            print(
                f"  Handler {i}: {type(handler).__name__} - {getattr(handler, 'baseFilename', 'no file')}"
            )


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
