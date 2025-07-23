import duckdb
import pandas as pd
import plotly.express as px
from typing import Optional

class MLflowAnalytics:
   """Analytics for MLflow experiments using DuckDB"""
   
   def __init__(self, db_path: str = "mlflow.duckdb"):
       self.db_path = db_path
   
   def get_model_comparison(self) -> pd.DataFrame:
       """Compare all models across all metrics"""
       with duckdb.connect(self.db_path) as conn:
           return conn.execute("""
               WITH model_metrics AS (
                   SELECT 
                       p.value as model_type,
                       m.key as metric,
                       AVG(m.value) as avg_value,
                       MIN(m.value) as min_value,
                       MAX(m.value) as max_value,
                       COUNT(*) as num_runs
                   FROM runs r
                   JOIN params p ON r.run_id = p.run_id AND p.key = 'model_type'
                   JOIN metrics m ON r.run_id = m.run_id
                   WHERE r.status = 'FINISHED'
                   GROUP BY p.value, m.key
               )
               PIVOT model_metrics 
               ON metric 
               USING FIRST(avg_value)
               ORDER BY f1_score DESC NULLS LAST
           """).fetchdf()
   
   def get_experiment_timeline(self) -> pd.DataFrame:
       """Get experiment timeline for visualization"""
       with duckdb.connect(self.db_path) as conn:
           return conn.execute("""
               SELECT 
                   DATE_TRUNC('hour', to_timestamp(start_time/1000)) as hour,
                   COUNT(*) as runs_count,
                   AVG(CASE WHEN m.key = 'f1_score' THEN m.value END) as avg_f1,
                   COUNT(DISTINCT p.value) as models_tested
               FROM runs r
               LEFT JOIN metrics m ON r.run_id = m.run_id AND m.key = 'f1_score'
               LEFT JOIN params p ON r.run_id = p.run_id AND p.key = 'model_type'
               GROUP BY hour
               ORDER BY hour
           """).fetchdf()
   
   def find_best_hyperparameters(self, model_type: str, metric: str = "f1_score") -> pd.DataFrame:
       """Find best hyperparameters for a specific model"""
       with duckdb.connect(self.db_path) as conn:
           return conn.execute(f"""
               WITH model_runs AS (
                   SELECT r.run_id
                   FROM runs r
                   JOIN params p ON r.run_id = p.run_id
                   WHERE p.key = 'model_type' AND p.value = '{model_type}'
                   AND r.status = 'FINISHED'
               ),
               ranked_runs AS (
                   SELECT 
                       mr.run_id,
                       m.value as metric_value,
                       RANK() OVER (ORDER BY m.value DESC) as rank
                   FROM model_runs mr
                   JOIN metrics m ON mr.run_id = m.run_id
                   WHERE m.key = '{metric}'
               )
               SELECT 
                   rr.rank,
                   rr.metric_value,
                   p.key as param_name,
                   p.value as param_value
               FROM ranked_runs rr
               JOIN params p ON rr.run_id = p.run_id
               WHERE rr.rank <= 5
               ORDER BY rr.rank, p.key
           """).fetchdf()