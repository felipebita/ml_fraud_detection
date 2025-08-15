# Testing Documentation

## FILES
./tests/unit/test_data_loader.py
./tests/unit/test_mlflow_analytics.py
./tests/unit/test_mlflow_duckdb_setup.py

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

## `tests/conftest.py`

*   **Purpose**: This file contains shared fixtures for the pytest tests.
*   **Usage**: It is used to define fixtures that can be used by multiple tests, such as temporary directories, mock objects, and sample data.
*   **Key Information**:
    *   **`temp_dir()`**: A fixture that creates a temporary directory for test artifacts.
    *   **`mock_mlflow_config()`**: A fixture that creates a mock MLflow configuration for testing.
    *   **`sample_experiment_data()`**: A fixture that creates a sample DataFrame with MLflow experiment data for analytics testing.

## `tests/unit/test_data_loader.py`

*   **Purpose**: This file contains unit tests for the data loader.
*   **Usage**: It is used to test the `load_data()` function in `src/data/data_loader.py` to ensure that it is working correctly.
*   **Key Information**:
    *   It tests for successful loading of a valid CSV file.
    *   It tests that a `FileNotFoundError` is raised for a non-existent file.
    *   It tests that a `ValueError` is raised for an empty CSV file.
    *   It tests that invalid rows are skipped and valid ones are loaded.
    *   It tests that an error is raised if no rows are valid.
    *   It directly tests the `TransactionSchema` Pydantic schema.

## `tests/unit/test_mlflow_analytics.py`

*   **Purpose**: This file contains unit tests for the MLflow analytics.
*   **Usage**: It is used to test the `MLflowAnalytics` class in `src/utils/mlflow_analytics.py` to ensure that it is working correctly.
*   **Key Information**:
    *   It tests the initialization of the `MLflowAnalytics` class.
    *   It tests the `get_model_comparison()` method.
    *   It tests the `get_experiment_timeline()` method.
    *   It tests the `find_best_hyperparameters()` method.

## `tests/unit/test_mlflow_duckdb_setup.py`

*   **Purpose**: This file contains unit tests for the MLflow DuckDB setup.
*   **Usage**: It is used to test the `MLflowConfig` and `MLflowDuckDBManager` classes in `src/utils/mlflow_duckdb_setup.py` to ensure that they are working correctly.
*   **Key Information**:
    *   It tests the initialization of the `MLflowConfig` class with default values and from environment variables.
    *   It tests the initialization of the `MLflowDuckDBManager` class.
    *   It tests the `setup_mlflow()` method with existing and new experiments.
    *   It tests the `get_connection()` method for both read-write and read-only connections.
    *   It tests the `query_experiments()` method.
    *   It tests the handling of connection failures.
