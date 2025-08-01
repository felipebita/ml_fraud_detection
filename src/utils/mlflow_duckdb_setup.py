import os
from pathlib import Path
from typing import cast

import duckdb
import mlflow
import pandas as pd

from src.utils.logger import LoggerContext, get_logger

# Initialize the structured logger
logger = get_logger(__name__)


class MLflowDuckDBConfig:
    """MLflow configuration with DuckDB backend"""

    def __init__(self) -> None:
        """Initialize configuration and create necessary directories."""
        # Use DuckDB for tracking
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "duckdb:///mlflow.duckdb")
        self.artifact_root = os.getenv("MLFLOW_ARTIFACT_ROOT", "./mlruns")
        self.experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "fraud_detection")

        # Extract DuckDB path
        self.db_path = self.tracking_uri.replace("duckdb:///", "")

        logger.info(
            "initializing_mlflow_config",
            tracking_uri=self.tracking_uri,
            artifact_root=self.artifact_root,
            db_path=self.db_path,
        )

        # Create directories
        Path(self.artifact_root).mkdir(parents=True, exist_ok=True)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def setup_mlflow(self) -> str:
        """Initialize MLflow with DuckDB backend."""
        with LoggerContext(logger, "setup_mlflow_backend"):
            try:
                # Set tracking URI
                mlflow.set_tracking_uri(self.tracking_uri)

                # Create or get experiment
                experiment = mlflow.get_experiment_by_name(self.experiment_name)
                if experiment is None:
                    logger.info(
                        "mlflow_experiment_not_found",
                        experiment_name=self.experiment_name,
                    )
                    experiment_id = mlflow.create_experiment(
                        self.experiment_name,
                        artifact_location=self.artifact_root,
                        tags={
                            "project": "fraud_detection",
                            "backend": "duckdb",
                            "version": "1.0",
                        },
                    )
                    logger.info(
                        "mlflow_experiment_created",
                        experiment_name=self.experiment_name,
                        experiment_id=experiment_id,
                    )
                else:
                    experiment_id = experiment.experiment_id
                    logger.info(
                        "mlflow_experiment_found",
                        experiment_name=self.experiment_name,
                        experiment_id=experiment_id,
                    )

                mlflow.set_experiment(self.experiment_name)
                return str(experiment_id)

            except Exception as e:
                logger.error("mlflow_setup_failed", error=str(e), exc_info=True)
                raise

    def get_duckdb_connection(self) -> duckdb.DuckDBPyConnection:
        """Get direct DuckDB connection for analytics."""
        logger.debug("connecting_to_duckdb", db_path=self.db_path)
        return duckdb.connect(self.db_path)

    def query_experiments(self, query: str) -> pd.DataFrame:
        """Query MLflow data using DuckDB."""
        with (
            LoggerContext(logger, "query_duckdb", query=query),
            self.get_duckdb_connection() as conn,
        ):
            df = conn.execute(query).fetchdf()
            logger.info("query_successful", num_rows=len(df))
            return cast(pd.DataFrame, df)

    def get_best_models(
        self, metric: str = "f1_score", top_n: int = 10
    ) -> pd.DataFrame:
        """Get best models using DuckDB's analytics capabilities."""
        query = f"""
        SELECT
            r.run_id,
            r.experiment_id,
            r.status,
            r.start_time,
            r.end_time,
            m.value as {metric},
            p.value as model_type
        FROM runs r
        JOIN metrics m ON r.run_id = m.run_id
        LEFT JOIN params p ON r.run_id = p.run_id AND p.key = 'model_type'
        WHERE m.key = '{metric}'
        AND r.status = 'FINISHED'
        ORDER BY m.value DESC
        LIMIT {top_n}
        """
        return self.query_experiments(query)

    def analyze_experiments(self) -> dict[str, pd.DataFrame]:
        """Analyze all experiments using DuckDB."""
        with (
            LoggerContext(logger, "analyze_experiments"),
            self.get_duckdb_connection() as conn,
        ):
            # Get experiment summary
            summary_query = """
            SELECT
                COUNT(DISTINCT experiment_id) as num_experiments,
                COUNT(DISTINCT run_id) as total_runs,
                COUNT(DISTINCT CASE WHEN status = 'FINISHED' THEN run_id END) as successful_runs,
                COUNT(DISTINCT CASE WHEN status = 'FAILED' THEN run_id END) as failed_runs
            FROM runs
            """
            summary = conn.execute(summary_query).fetchdf()

            # Get metrics summary
            metrics_query = """
            SELECT
                key as metric_name,
                COUNT(*) as count,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                STDDEV(value) as std_value
            FROM metrics
            GROUP BY key
            ORDER BY count DESC
            """
            metrics = conn.execute(metrics_query).fetchdf()

            # Get model type distribution
            models_query = """
            SELECT
                p.value as model_type,
                COUNT(DISTINCT r.run_id) as run_count,
                AVG(m.value) as avg_f1_score
            FROM runs r
            JOIN params p ON r.run_id = p.run_id
            JOIN metrics m ON r.run_id = m.run_id
            WHERE p.key = 'model_type'
            AND m.key = 'f1_score'
            AND r.status = 'FINISHED'
            GROUP BY p.value
            ORDER BY avg_f1_score DESC
            """
            models = conn.execute(models_query).fetchdf()

            logger.info(
                "experiment_analysis_complete",
                num_experiments=summary["num_experiments"][0],
                total_runs=summary["total_runs"][0],
            )
            return {"summary": summary, "metrics": metrics, "models": models}


# Singleton instance
mlflow_duckdb_config = MLflowDuckDBConfig()


def setup_mlflow_duckdb() -> None:
    """Setup MLflow with DuckDB backend"""
    mlflow_duckdb_config.setup_mlflow()


if __name__ == "__main__":
    logger.info("running_mlflow_duckdb_setup_script")
    setup_mlflow_duckdb()
    logger.info(
        "mlflow_duckdb_backend_setup_complete",
        tracking_uri=mlflow_duckdb_config.tracking_uri,
        artifact_root=mlflow_duckdb_config.artifact_root,
        experiment_name=mlflow_duckdb_config.experiment_name,
        db_path=mlflow_duckdb_config.db_path,
    )

    # Example usage
    logger.info("logging_test_run_to_mlflow")
    try:
        with mlflow.start_run(run_name="duckdb_setup_test_run") as run:
            mlflow.log_param("test_param", "duckdb_value")
            mlflow.log_metric("test_metric", 0.88)
        logger.info("test_run_logged_successfully", run_id=run.info.run_id)
    except Exception as e:
        logger.error("failed_to_log_test_run", error=str(e), exc_info=True)
