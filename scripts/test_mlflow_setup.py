# scripts/test_mlflow_setup.py
#!/usr/bin/env python3
"""Test MLflow setup using the centralized configuration."""

import sys

import mlflow

from src.utils.logger import get_logger
from src.utils.mlflow_duckdb_setup import setup_mlflow_duckdb

# Initialize logger
logger = get_logger(__name__)


def test_mlflow_connection():
    """Test if MLflow is properly configured by setting it up and logging a test run."""
    try:
        # Setup MLflow using the centralized function
        setup_mlflow_duckdb()
        logger.info("mlflow_setup_initialized_from_config")

        # Create a test run
        logger.info("starting_mlflow_test_run")
        with mlflow.start_run(run_name="mlflow_setup_test") as run:
            run_id = run.info.run_id
            mlflow.log_param("test_param", "config_value")
            mlflow.log_metric("test_metric", 0.99)
            logger.info("mlflow_test_run_logged", run_id=run_id)

        logger.info(
            "mlflow_setup_successful",
            run_id=run_id,
            tracking_uri=mlflow.get_tracking_uri(),
            ui_hint="Check the MLflow UI to verify the test run.",
        )
        return True

    except Exception as e:
        logger.error("mlflow_setup_failed", error=str(e), exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("executing_mlflow_setup_test")
    success = test_mlflow_connection()
    if success:
        logger.info("mlflow_setup_test_succeeded")
    else:
        logger.error("mlflow_setup_test_failed")
    sys.exit(0 if success else 1)
