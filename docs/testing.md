# Testing Documentation

#### Run all tests
make test

#### Run specific test file
pytest tests/unit/test_mlflow_analytics.py -v

#### Run with coverage
pytest --cov=src --cov-report=html

## Test Logging

The project is configured to have separate log files for the application and the tests.

*   **Application Logs:** `logs/fraud_detection.log`
*   **Test Logs:** `logs/pytest.log`

This is achieved by a special configuration in `src/utils/logger.py` that detects when `pytest` is running and modifies the logging configuration accordingly.

When `pytest` is running, the `setup_logging` function in `src/utils/logger.py` does the following:

1.  It **preserves** any existing logging handlers that `pytest` has configured.
2.  It adds a **dedicated handler** for the `logs/pytest.log` file.
3.  It forces all loggers to **propagate** to the root logger, which ensures that all logs (including those from third-party libraries) are captured in the `logs/pytest.log` file.

This setup ensures that the test logs are captured in a separate file without interfering with the application's logging.

## FILES
- `./tests/`
    - `./tests/conftest.py`
    - `./tests/integration/`
        - `./tests/integration/test_feast_basic.py`
    - `./tests/unit/`
        - `./tests/unit/test_data_loader.py`
        - `./tests/unit/test_data_profiler.py`
        - `./tests/unit/test_data_splitter.py`
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

#### `tests/integration/test_feast_basic.py`

*   **Purpose**: This file contains integration tests for the Feast feature store.
*   **Usage**: It verifies that the feature store is correctly configured and that features can be retrieved from both the online and offline stores.
*   **Key Information**:
    *   It tests the loading of feature definitions.
    *   It tests the retrieval of historical features from the offline store.
    *   It tests the retrieval of online features from the online store.
    *   It tests for consistency between the online and offline stores.

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

#### `tests/unit/test_data_processing.py`

*   **Purpose**: This file contains unit tests for the `DataProcessor` class from `src/data/data_processing.py`.
*   **Usage**: It verifies the correctness of each data transformation step.
*   **Key Information**:
    *   It uses `pytest` fixtures to create a `DataProcessor` instance and a sample DataFrame.
    *   `test_standardize_converts_type_and_adds_timestamp`: Verifies that the `standardize` method correctly converts the `type` column to a categorical dtype and creates the `event_timestamp` column with the correct values.
    *   `test_filter_transaction_types`: Ensures that the `filter_transaction_types` method correctly filters the DataFrame to only include `CASH_OUT` and `TRANSFER` types.
    *   `test_encode_transaction_type`: Checks that the `encode_transaction_type` method correctly encodes the `type` column into a binary (0/1) format.

#### `tests/unit/test_data_profiler.py`

*   **Purpose**: This file contains a comprehensive suite of unit tests for the `DataProfiler` class from `src/data/data_profiler.py`.
*   **Usage**: It verifies that the data profiling and report generation logic is correct under a wide variety of conditions.
*   **Key Information**:
    *   It uses `pytest` fixtures to create a sample DataFrame and a `DataProfiler` instance for testing.
    *   It tests the successful generation of the main profile, ensuring all expected statistical sections (`numerical_stats`, `categorical_stats`, etc.) are present.
    *   It verifies that the profile can be correctly exported to a JSON file.
    *   It includes numerous tests for specific data quality checks, such as the detection of high missing values, constant columns, and transaction balance inconsistencies.
    *   It tests edge cases for the temporal and class distribution analyses, such as when the relevant columns (`step`, `isFraud`) are missing or contain no positive cases.

#### `tests/unit/test_data_validator.py`

*   **Purpose**: This file contains unit tests for the data validator.
*   **Usage**: It is used to test the `DataValidator` class in `src/data/data_validator.py` to ensure that it is working correctly.
*   **Key Information**:
    *   It tests for successful validation of a valid DataFrame.
    *   It tests that validation fails for incorrect data types, out-of-range values, disallowed categories, missing columns, and extra columns.

#### `tests/unit/test_data_splitter.py`

*   **Purpose**: This file contains unit tests for the `DataSplitter` class.
*   **Usage**: It verifies the core logic of the chronological data split without depending on the actual file system.
*   **Key Information**:
    *   It uses a mock configuration and an in-memory sample DataFrame to ensure the test is isolated.
    *   It patches `pandas.read_parquet` and `pandas.to_parquet` to prevent any actual file I/O.
    *   It verifies that the data is split according to the configured ratio (e.g., 80/20).
    *   Most importantly, it asserts that all data in the training set is chronologically earlier than any data in the test set, confirming the integrity of the time-based split.

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
