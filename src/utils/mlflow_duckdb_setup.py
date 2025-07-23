import os
import duckdb
import mlflow
from pathlib import Path
from typing import Optional, Dict, List
import pandas as pd
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)

class MLflowDuckDBConfig:
   """MLflow configuration with DuckDB backend"""
   
   def __init__(self):
       # Use DuckDB for tracking
       self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "duckdb:///mlflow.duckdb")
       self.artifact_root = os.getenv("MLFLOW_ARTIFACT_ROOT", "./mlruns")
       self.experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "fraud_detection")
       
       # Extract DuckDB path
       self.db_path = self.tracking_uri.replace("duckdb:///", "")
       
       # Create directories
       Path(self.artifact_root).mkdir(parents=True, exist_ok=True)
       Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
       
   def setup_mlflow(self) -> str:
       """Initialize MLflow with DuckDB backend"""
       try:
           # Set tracking URI
           mlflow.set_tracking_uri(self.tracking_uri)
           
           # Create or get experiment
           experiment = mlflow.get_experiment_by_name(self.experiment_name)
           if experiment is None:
               experiment_id = mlflow.create_experiment(
                   self.experiment_name,
                   artifact_location=self.artifact_root,
                   tags={
                       "project": "fraud_detection",
                       "backend": "duckdb",
                       "version": "1.0"
                   }
               )
               logger.info(f"Created experiment: {self.experiment_name} (ID: {experiment_id})")
           else:
               experiment_id = experiment.experiment_id
               
           mlflow.set_experiment(self.experiment_name)
           return experiment_id
           
       except Exception as e:
           logger.error(f"Error setting up MLflow with DuckDB: {str(e)}")
           raise
   
   def get_duckdb_connection(self) -> duckdb.DuckDBPyConnection:
       """Get direct DuckDB connection for analytics"""
       return duckdb.connect(self.db_path)
   
   def query_experiments(self, query: str) -> pd.DataFrame:
       """Query MLflow data using DuckDB"""
       with self.get_duckdb_connection() as conn:
           return conn.execute(query).fetchdf()
   
   def get_best_models(self, metric: str = "f1_score", top_n: int = 10) -> pd.DataFrame:
       """Get best models using DuckDB's analytics capabilities"""
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
   
   def analyze_experiments(self) -> Dict:
       """Analyze all experiments using DuckDB"""
       with self.get_duckdb_connection() as conn:
           # Get experiment summary
           summary = conn.execute("""
               SELECT 
                   COUNT(DISTINCT experiment_id) as num_experiments,
                   COUNT(DISTINCT run_id) as total_runs,
                   COUNT(DISTINCT CASE WHEN status = 'FINISHED' THEN run_id END) as successful_runs,
                   COUNT(DISTINCT CASE WHEN status = 'FAILED' THEN run_id END) as failed_runs
               FROM runs
           """).fetchdf()
           
           # Get metrics summary
           metrics = conn.execute("""
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
           """).fetchdf()
           
           # Get model type distribution
           models = conn.execute("""
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
           """).fetchdf()
           
           return {
               "summary": summary,
               "metrics": metrics,
               "models": models
           }

# Singleton instance
mlflow_duckdb_config = MLflowDuckDBConfig()