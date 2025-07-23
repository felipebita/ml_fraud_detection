#!/bin/bash
# scripts/start_mlflow_duckdb.sh

# Load environment variables
if [ -f ".env" ]; then
source .env
else
echo "Warning: .env file not found, using defaults"
fi

# Set defaults if not in .env
DB_PATH="${MLFLOW_DB_PATH:-mlflow.duckdb}"
MLFLOW_PORT="${MLFLOW_PORT:-5000}"
MLFLOW_HOST="${MLFLOW_HOST:-127.0.0.1}"
MLFLOW_ARTIFACT_ROOT="${MLFLOW_ARTIFACT_ROOT:-./mlruns}"

echo "Starting MLflow server with DuckDB backend..."
echo "Database: $DB_PATH"
echo "Artifacts: $MLFLOW_ARTIFACT_ROOT"
echo "URL: http://$MLFLOW_HOST:$MLFLOW_PORT"

# Create directories if they don't exist
mkdir -p $(dirname $DB_PATH)
mkdir -p $MLFLOW_ARTIFACT_ROOT

# Note: MLflow server doesn't directly support DuckDB yet,
# so we use SQLite URI which DuckDB can also handle
mlflow server \
--backend-store-uri sqlite:///$DB_PATH \
--default-artifact-root $MLFLOW_ARTIFACT_ROOT \
--host $MLFLOW_HOST \
--port $MLFLOW_PORT \
--serve-artifacts