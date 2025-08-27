# Testing Documentation

#### Run all tests
make test

#### Run specific test file
pytest tests/unit/test_mlflow_analytics.py -v

#### Run with coverage
pytest --cov=src --cov-report=html

## FILES
- `./tests/`
    - `./tests/conftest.py`
    - `./tests/integration/`
    - `./tests/unit/`
    - `./tests/unit/test_data_loader.py`
    - `./tests/unit/test_data_validator.py`
    - `./tests/unit/test_mlflow_analytics.py`
    - `./tests/unit/test_mlflow_duckdb_setup.py`

## `tests/`

*   **Purpose**: This directory contains all the tests for the project, including unit and integration tests.
*   **Usage**: It is used to ensure the quality and correctness of the code.
*   **Key Information**:
    *   It is organized into `unit/` and `integration/` subdirectories.
    *   `conftest.py` provides shared fixtures for all tests.

### `tests/conftest.py`

*   **Purpose**: This file contains shared fixtures for the pytest tests.
*   **Usage**: It is used to define fixtures that can be used by multiple tests, such as temporary directories, mock objects, and sample data.
*   **Key Information**:
    *   **`temp_dir()`**: A fixture that creates a temporary directory for test artifacts.
    *   **`mock_mlflow_config()`**: A fixture that creates a mock MLflow configuration for testing.
    *   **`sample_experiment_data()`**: A fixture that creates a sample DataFrame with MLflow experiment data for analytics testing.

### `tests/integration/`

*   **Purpose**: This directory contains all the integration tests for the project.
*   **Usage**: It is used to test the interaction between different components of the application.
*   **Key Information**:
    *   Tests are organized by the workflow they are testing.

### `tests/unit/`

*   **Purpose**: This directory contains all the unit tests for the project.
*   **Usage**: It is used to test individual components of the application in isolation.
*   **Key Information**:
    *   Tests are organized by the module they are testing.

#### `tests/unit/test_data_loader.py`

*   **Purpose**: This file contains unit tests for the data loader.
*   **Usage**: It is used to test the `load_data()` function in `src/data/data_loader.py` to ensure that it is working correctly.
*   **Key Information**:
    *   It tests for successful loading of a valid CSV file.
    *   It tests that a `FileNotFoundError` is raised for a non-existent file.
    *   It tests that a `ValueError` is raised for an empty CSV file.
    *   It tests that invalid rows are skipped and valid ones are loaded.
    *   It tests that an error is raised if no rows are valid.
    *   It directly tests the `TransactionSchema` Pydantic schema.

#### `tests/unit/test_data_validator.py`

*   **Purpose**: This file contains unit tests for the data validator.
*   **Usage**: It is used to test the `DataValidator` class in `src/data/data_validator.py` to ensure that it is working correctly.
*   **Key Information**:
    *   It tests for successful validation of a valid DataFrame.
    *   It tests that validation fails for incorrect data types, out-of-range values, disallowed categories, missing columns, and extra columns.
    *   It tests the standardization of column types.

#### `tests/unit/test_mlflow_analytics.py`

*   **Purpose**: This file contains unit tests for the MLflow analytics.
*   **Usage**: It is used to test the `MLflowAnalytics` class in `src/utils/mlflow_analytics.py` to ensure that it is working correctly.
*   **Key Information**:
    *   It tests the initialization of the `MLflowAnalytics` class.
    *   It tests the `get_model_comparison()` method.
    *   It tests the `get_experiment_timeline()` method.
    *   It tests the `find_best_hyperparameters()` method.

#### `tests/unit/test_mlflow_duckdb_setup.py`

*   **Purpose**: This file contains unit tests for the MLflow DuckDB setup.
*   **Usage**: It is used to test the `MLflowConfig` and `MLflowDuckDBManager` classes in `src/utils/mlflow_duckdb_setup.py` to ensure that they are working correctly.
*   **Key Information**:
    *   It tests the initialization of the `MLflowConfig` class with default values and from environment variables.
    *   It tests the initialization of the `MLflowDuckDBManager` class.
    *   It tests the `setup_mlflow()` method with existing and new experiments.
    *   It tests the `get_connection()` method for both read-write and read-only connections.
    *   It tests the `query_experiments()` method.
    *   It tests the handling of connection failures.
