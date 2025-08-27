# Logging System

This project uses a structured logging setup powered by `structlog` to ensure all log outputs are consistent, machine-readable, and informative. This guide explains how the logging system is configured, how to use it, and how to extend it.

## 1. Overview

Structured logging is crucial for monitoring and debugging applications, especially in a production environment. Instead of plain text logs, we use structured logs (in JSON format for files) which can be easily parsed, queried, and visualized by log management systems.

Our logging setup provides:
-   **Centralized Configuration**: All logging settings are defined in a single `logging_config.yaml` file.
-   **Multiple Handlers**: Logs are sent to the console, a general log file, and a separate error log file.
-   **Structured Output**: Logs are enriched with context, such as timestamps, log levels, and function names.
-   **Specialized Loggers**: Helper functions are available to log common, structured data like model metrics or dataset information.

## 2. Configuration (`configs/logging_config.yaml`)

The entire logging behavior is controlled by `configs/logging_config.yaml`. Here’s a breakdown of its main sections:

### `formatters`
This section defines how log records are formatted.

-   `default`: A simple, human-readable format for console output.
-   `json`: A JSON formatter for file outputs, making logs easy to parse.
-   `detailed`: A more verbose format used for the error log file.

### `handlers`
This section defines where the logs are sent.

-   `console`: Sends logs to the standard output (your terminal).
-   `file`: Writes logs to `logs/fraud_detection.log`. It uses a `RotatingFileHandler` to keep the file size in check.
-   `error_file`: Writes only `ERROR` level logs and above to `logs/errors.log`.

### `loggers`
This section ties specific modules to handlers and log levels.

-   You can define loggers for different parts of the application (e.g., `src`, `src.models`, `src.data`).
-   Each logger can have its own log level and set of handlers.
-   `propagate: false` prevents log messages from being passed up to the root logger, avoiding duplicate logs.

### `root`
This is the fallback logger. Any logger not explicitly defined will inherit its configuration from the root.

## 3. Usage

Using the logging system is straightforward.

### Getting a Logger Instance
To get a logger in any module, use the `get_logger` function from `src.utils.logger`:

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
```

### Logging Messages
You can log messages at different severity levels:

```python
logger.debug("This is a detailed message for debugging.")
logger.info("An informational message.")
logger.warning("A warning about a potential issue.")
logger.error("An error occurred.", exc_info=True) # exc_info=True adds traceback
logger.critical("A critical error. The application might crash.")
```

### Using the `LoggerContext`
For logging the duration and status of an operation, use the `LoggerContext` manager. It automatically logs the start, completion, and any failures.

```python
from src.utils.logger import LoggerContext

with LoggerContext(logger, "my_long_operation", param1="value"):
    # Your code here
    ...
```

**Output:**
```
2025-08-27 10:00:00 - __main__ - INFO - my_long_operation_started - param1='value'
2025-08-27 10:00:05 - __main__ - INFO - my_long_operation_completed - duration_seconds=5.0 - param1='value'
```

### Specialized Loggers
The `src.utils.logger` module provides helper functions for logging common, structured data.

-   **`log_data_info(logger, df, "my_dataset")`**: Logs key information about a DataFrame, such as its shape, columns, and memory usage.
-   **`log_model_metrics(logger, metrics_dict, "my_model")`**: Logs model performance metrics from a dictionary.
-   **`log_prediction(logger, prediction_dict)`**: Logs the details of a single prediction for auditing purposes.

## 4. Log Output Examples

### Console Output (from `default` formatter)
```
2025-08-27 10:00:00 - __main__ - INFO - This is an info message
```

### File Output (from `json` formatter in `logs/fraud_detection.log`)
```json
{"asctime": "2025-08-27 10:00:00,123", "name": "__main__", "levelname": "INFO", "message": "This is an info message", "pathname": "src/main.py", "lineno": 42}
```

## 5. Best Practices

-   **Use `get_logger(__name__)`**: This uses the module's name for the logger, making it easy to track where log messages originate from.
-   **Be Descriptive**: Your log messages should be clear and provide context.
-   **Log at the Right Level**:
    -   `DEBUG`: For detailed, diagnostic information.
    -   `INFO`: For general operational messages.
    -   `WARNING`: For unexpected events or potential problems.
    -   `ERROR`: For errors that prevent a specific operation from completing.
    -   `CRITICAL`: For severe errors that could terminate the application.
-   **Don't Log Sensitive Data**: Never log passwords, API keys, or personal user information.
