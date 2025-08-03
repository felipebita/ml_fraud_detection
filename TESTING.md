# Testing Documentation

## Test Structure

tests/
├── unit/ # Unit tests for individual components
│ ├── test_mlflow_analytics.py # Tests for MLflowAnalytics class
│ └── test_mlflow_duckdb_setup.py # Tests for MLflow configuration
├── integration/ # Integration tests (coming soon)
└── conftest.py # Shared test fixtures


## What We Test

### MLflow Analytics (`test_mlflow_analytics.py`)
- **Class**: `MLflowAnalytics`
- **Coverage**: Connection handling, query execution, data retrieval
- **Key Tests**:
- `test_initialization`: Verifies proper dependency injection
- `test_get_model_comparison`: Tests model comparison queries
- `test_get_experiment_timeline`: Tests timeline data retrieval
- `test_find_best_hyperparameters`: Tests parameter optimization queries

### MLflow Setup (`test_mlflow_duckdb_setup.py`)
- **Classes**: `MLflowConfig`, `MLflowDuckDBManager`
- **Coverage**: Configuration, MLflow initialization, connection management
- **Key Tests**:
- Config initialization from env vars
- Experiment creation/retrieval
- Connection handling and failures

## Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_mlflow_analytics.py -v

# Run with coverage
pytest --cov=src --cov-report=html
