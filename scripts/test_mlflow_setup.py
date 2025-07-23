# scripts/test_mlflow_setup.py
#!/usr/bin/env python3
"""Test MLflow setup"""

import mlflow
import sys

def test_mlflow_connection():
    """Test if MLflow is properly configured"""
    try:
        # Set tracking URI
        mlflow.set_tracking_uri("sqlite:///mlflow.duckdb")
        
        # Create a test run
        with mlflow.start_run() as run:
            mlflow.log_param("test_param", "test_value")
            mlflow.log_metric("test_metric", 0.99)
            
        print("✅ MLflow setup successful!")
        print(f"Run ID: {run.info.run_id}")
        print("Check the MLflow UI at http://localhost:5000")
        return True
    
    except Exception as e:
        print(f"❌ MLflow setup failed: {e}")
        return False

if __name__ == "__main__":
    success = test_mlflow_connection()
    sys.exit(0 if success else 1)