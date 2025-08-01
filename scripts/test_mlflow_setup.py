# scripts/test_mlflow_setup.py
#!/usr/bin/env python3
"""Test MLflow setup"""

import sys

import mlflow

from src.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


def test_mlflow_connection():
    """Test if MLflow is properly configured"""
    try:
        # Set tracking URI
        tracking_uri = "sqlite:///mlflow.duckdb"
        mlflow.set_tracking_uri(tracking_uri)
        logger.info("mlflow_tracking_uri_set", uri=tracking_uri)

        # Create a test run
        logger.info("starting_mlflow_test_run")
        with mlflow.start_run() as run:
            run_id = run.info.run_id
            mlflow.log_param("test_param", "test_value")
            mlflow.log_metric("test_metric", 0.99)
            logger.info("mlflow_test_run_logged", run_id=run_id)

        logger.info(
            "mlflow_setup_successful",
            run_id=run_id,
            ui_hint="Check the MLflow UI at http://localhost:5000",
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
