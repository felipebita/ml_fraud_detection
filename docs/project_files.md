# Project File Documentation

This file provides a comprehensive overview of all files in the project, including their purpose, usage, and any other relevant information.

## Files

- `./.github/`
    - `./.github/workflows/ci.yml`
- `./configs/`
    - `./configs/logging_config.yaml`
- `./data/`
    - `./data/profiling_results.json`
    - `./data/features/`
    - `./data/processed/`
    - `./data/raw/`
- `./docs/`
    - `./docs/business.md`
    - `./docs/index.md`
    - `./docs/project_files.md`
    - `./docs/PROJECT_PLAN.md`
    - `./docs/TESTING.md`
- `./duckdb:` ?
- `./dhtmlcov/`
- `./logs/`
    - `./logs/fraud_detection.log`
- `./models/`
- `./notebooks/`
    - `./notebooks/01_eda.ipynb`
- `./scripts/`
    - `./scripts/start_mlflow_duckdb.sh`
    - `./scripts/test_mlflow_setup.py`
    - `./scripts/test_profiler.py`
- `./src/`
    - `./src/__init__.py`
    - `./src/data/`
        - `./src/data/data_loader.py`
        - `./src/data/data_profiler.py`
        - `./src/data/data_validator.py`
    - `./src/utils/`
        - `./src/utils/logger.py`
        - `./src/utils/mlflow_analytics.py`
        - `./src/utils/mlflow_duckdb_setup.py`
- `./tests/`
    - `./tests/conftest.py`
    - `./tests/integration`
    - `./tests/unit/test_data_loader.py`
    - `./tests/unit/test_data_validator.py`
    - `./tests/unit/test_mlflow_analytics.py`
    - `./tests/unit/test_duckdb_setup.py`
- `./.env`
- `./.env.example`
- `./.gitignore`
- `./.pre-commit-config.yaml`
- `./coverage.xml`
- `./Makefile`
- `./mkdocs.yml`
- `./mlflow.duckdb`
- `./pyproject.toml`
- `./README.md`
- `./uv.lock`


## `data/`

*   **Purpose**: This directory contains the data for the project.
*   **Key Directories**:
    *   `raw`: Contains the raw data.
    *   `processed`: Contains the processed data.
    *   `features`: Contains the engineered features.

### `data/raw/`

*   **Purpose**: This directory contains the raw, immutable data for the project.
*   **Usage**: Data in this directory should be treated as read-only. No modifications should be made to the files in this directory.

### `data/processed/`

*   **Purpose**: This directory contains the processed and cleaned data.
*   **Usage**: The data in this directory is the result of cleaning and preprocessing the raw data. It is the input for the feature engineering step.

### `data/features/`

*   **Purpose**: This directory contains the engineered features.
*   **Usage**: The data in this directory is the result of the feature engineering process. It is the input for the model training.

### `data/profiling_results.json`

*   **Purpose**: This file contains the results of the data profiling.
*   **Usage**: It is used to store the data profile report in a JSON format.

## `.gitignore`

*   **Purpose**: This file specifies intentionally untracked files that Git should ignore.
*   **Usage**: It's used to avoid committing files that are not necessary for the project, such as environment variables, large data files, and model experiment files.
*   **Key Information**:
    *   **Credentials**: Ignores `.env` files, `.key` files, and `credentials/` directories to prevent sensitive information from being committed.
    *   **Data**: Ignores large data files but includes sample data for portfolio purposes.
    *   **Models**: Ignores experimental and staging models but includes final models.
    *   **MLflow**: Ignores MLflow tracking data but includes documentation and screenshots.
    *   **Notebooks**: Keeps notebook outputs for portfolio purposes.
    *   **Outputs**: Includes example outputs such as reports and logs.

## `.pre-commit-config.yaml`

*   **Purpose**: This file configures the pre-commit hooks that are run before each commit to ensure code quality and consistency.
*   **Usage**: It helps to automate code formatting, linting, and other checks to catch issues before they are committed to the repository.
*   **Key Information**:
    *   **`pre-commit-hooks`**: Includes basic checks like fixing trailing whitespace and end-of-file issues, validating YAML files, checking for large files, merge conflicts, private keys, and valid Python syntax. It also checks for docstrings and debug statements.
    *   **`black`**: An opinionated code formatter for Python to ensure consistent code style.
    *   **`ruff`**: A fast Python linter that checks for a wide range of errors and style issues, and automatically fixes them.
    *   **`mypy`**: A static type checker for Python, configured to check the `src/` directory for type errors, ignoring missing imports and not enforcing strict optional types.

## `pyproject.toml`

*   **Purpose**: This file is the unified configuration file for the project, specifying metadata, dependencies, and tool settings.
*   **Usage**: It is used by `pip` and other tools to manage the project's packaging, dependencies, and development environment.
*   **Key Information**:
    *   **`[project]`**: Defines core project metadata like name, version, author, and dependencies.
    *   **`[project.optional-dependencies]`**: Specifies optional dependencies for different environments, such as `dev`, `notebook`, and `monitoring`.
    *   **`[project.scripts]`**: Creates command-line entry points for the project.
    *   **`[tool.black]`**: Configuration for the Black code formatter.
    *   **`[tool.ruff]`**: Configuration for the Ruff linter.
    *   **`[tool.mypy]`**: Configuration for the Mypy static type checker.
    *   **`[tool.pytest.ini_options]`**: Configuration for the Pytest testing framework.
    *   **`[tool.coverage.run]`**: Configuration for code coverage with `pytest-cov`.
    *   **`[tool.isort]`**: Configuration for the `isort` import sorter.
    *   **`[tool.bandit]`**: Configuration for the Bandit security linter.

## `.env.example` and `.env`

*   **Purpose**: These files are used to manage environment variables for the project.
*   **Usage**:
    *   `.env.example` is a template file that shows which environment variables are needed for the project. It should be committed to the repository.
    *   `.env` is the actual file that contains the environment variables. It should not be committed to the repository and should be listed in the `.gitignore` file.
*   **Key Information**:
    *   These files are used to store sensitive information, such as API keys and database credentials.

## `coverage.xml` and `.coverage`

*   **Purpose**: These files are generated by `pytest-cov` and contain the code coverage data.
*   **Usage**:
    *   `.coverage` is the raw coverage data file.
    *   `coverage.xml` is the coverage report in XML format, which can be used by CI/CD tools.
*   **Key Information**:
    *   These files are usually ignored by Git.

## `mkdocs.yml`

*   **Purpose**: This file is the configuration file for the `mkdocs` documentation generator.
*   **Usage**: It is used to configure the site name, theme, navigation, and other settings for the project documentation.

## `mlflow.duckdb`

*   **Purpose**: This is the DuckDB database file used by MLflow.
*   **Usage**: It stores all the experiment tracking data, including runs, parameters, metrics, and artifacts.
*   **Key Information**:
    *   This file is a binary file and should not be manually edited.

## `README.md`

*   **Purpose**: This file provides a high-level overview of the project, including the business context, project goals, and scope of analysis.
*   **Usage**: It is the first file that users see when they visit the project's repository, so it should contain essential information about the project.
*   **Key Information**:
    *   **Executive Summary**: Provides a brief overview of the project.
    *   **Business Context**: Describes the business problem and the monetization model.
    *   **Project Goals**: Outlines the objectives of the project.
    *   **Scope of Analysis**: Details the framework for evaluating the model's success.

## `uv.lock`

*   **Purpose**: This file is the lock file for the `uv` package manager. It records the exact versions of all dependencies used in the project.
*   **Usage**: It ensures that the project has a reproducible environment by locking the versions of all dependencies, which prevents unexpected changes from new releases.
*   **Key Information**:
    *   This file is automatically generated and managed by `uv`. It should not be edited manually.

## `models/`

*   **Purpose**: This directory contains the trained models.
*   **Usage**: It is used to store the serialized model artifacts that are ready for deployment.

## `mlruns/`

*   **Purpose**: This directory contains the MLflow tracking data.
*   **Usage**: It is used by MLflow to store the experiment data, including parameters, metrics, and artifacts. This directory should not be manually edited.

## `logs/`

*   **Purpose**: This directory contains the log files for the project.
*   **Key Files**:
    *   `fraud_detection.log`: The main log file for the project.

## `htmlcov/`

*   **Purpose**: This directory contains the HTML report for the code coverage.
*   **Usage**: It is generated by `pytest-cov` and can be used to view the code coverage of the tests.

## `docs/`

*   **Purpose**: This directory contains the documentation for the project.
*   **Key Files**:
    *   `business.md`: Describes the business context of the project.
    *   `index.md`: The main documentation page.
    *   `project_files.md`: This file.
    *   `PROJECT_PLAN.md`: The project plan.
    *   `TESTING.md`: The testing strategy.

## `scripts/`

*   **Purpose**: This directory contains standalone scripts for various tasks, such as starting services or running tests.

### `scripts/start_mlflow_duckdb.sh`

*   **Purpose**: This script starts the MLflow tracking server with a DuckDB backend.
*   **Usage**: It is used to launch the MLflow server, which is essential for logging experiments, tracking model performance, and managing the machine learning lifecycle.
*   **Key Information**:
    *   It loads environment variables from a `.env` file.
    *   It sets default values for the database path, MLflow port, host, and artifact root if they are not defined in the `.env` file.
    *   It creates the necessary directories for the database and artifacts.
    *   It starts the MLflow server using the specified configurations.

### `scripts/test_mlflow_setup.py`

*   **Purpose**: This script tests the MLflow setup to ensure that it is properly configured and accessible.
*   **Usage**: It can be run to verify that the MLflow tracking server is running and that experiments can be logged.
*   **Key Information**:
    *   It sets the MLflow tracking URI to the DuckDB database.
    *   It starts a test run, logs a parameter and a metric, and then ends the run.
    *   It prints a success message if the connection is successful, or an error message if it fails.

### `scripts/test_profiler.py`

*   **Purpose**: This script tests the data profiler with sample data.
*   **Usage**: It can be run to verify that the data profiler is working correctly and to generate a sample profiling report.
*   **Key Information**:
    *   It creates a sample DataFrame with random data.
    *   It adds some data quality issues to the DataFrame, such as missing values.
    *   It runs the data profiler on the sample DataFrame and exports the results to a JSON file.

## `notebooks/`

*   **Purpose**: This directory contains Jupyter notebooks for exploratory data analysis (EDA), model analysis, and experimentation.

### `notebooks/01_eda.ipynb`

*   **Purpose**: This Jupyter notebook is used for exploratory data analysis (EDA) of the fraud detection dataset.
*   **Usage**: It provides an interactive environment for data scientists and developers to explore the data, visualize distributions, and identify patterns and anomalies.
*   **Key Information**:
    *   **Data Loading**: Loads the dataset and provides an initial overview of the data.
    *   **Data Profiling**: Performs data profiling to understand the data types, missing values, and other quality issues.
    *   **Fraud Analysis**: Analyzes the distribution of fraud and non-fraud transactions.
    *   **Feature Engineering**: Creates new features based on the analysis of the data.
    *   **Temporal Analysis**: Analyzes the temporal patterns of fraud.

## `src/`

*   **Purpose**: This is the main source code directory for the project.

### `src/__init__.py`

*   **Purpose**: This file initializes the `src` package and sets up the logging for the project.
*   **Usage**: It is automatically imported when any module from the `src` package is imported.
*   **Key Information**:
    *   It initializes the logging for the project by calling the `setup_logging()` function from `src.utils.logger`.
    *   It gets the logging configuration from environment variables.
    *   It creates a package-level logger.

### `src/data/`

### `src/data/data_loader.py`

*   **Purpose**: This script loads and validates the raw data.
*   **Usage**: It is used to load the raw data from a CSV file, validate it against a Pydantic schema, and save the validated data to a Parquet file.
*   **Key Information**:
    *   **`TransactionSchema` class**: A Pydantic schema for validating the structure and types of a single transaction row.
    *   **`load_data()`**: Loads transaction data from a CSV file, validates it against the `TransactionSchema`, and returns a clean DataFrame.
    *   When run as a standalone script, it loads the raw data, validates it, and saves the validated data to a Parquet file in the `data/processed` directory.

### `src/data/data_validator.py`

*   **Purpose**: This script contains the `DataValidator` class, which is used to perform data quality checks on the loaded data.
*   **Usage**: It is used to validate the data against a set of rules, such as checking for missing values, duplicate records, and outliers.
*   **Key Information**:
    *   It uses the `pandera` library to define and execute the data validation rules.
    *   It generates a data quality report that summarizes the validation results.

### `src/data/data_profiler.py`

*   **Purpose**: This script profiles the data to provide a comprehensive overview of the data quality and characteristics.
*   **Usage**: It is used to generate a data profile report that includes basic information, data types, missing values, numerical and categorical stats, data quality issues, class distribution, and temporal analysis.
*   **Key Information**:
    *   **`DataProfiler` class**: A class that encapsulates the data profiling functionality.
    *   **`generate_profile()`**: Generates a comprehensive data profile.
    *   **`export_profile()`**: Exports the profile to a JSON file.
    *   **`get_summary_report()`**: Generates a human-readable summary report.
    *   **`quick_profile()`**: A convenience function to quickly generate and print a data profile.

### `src/utils/`

#### `src/utils/logger.py`

*   **Purpose**: This file provides a centralized logging setup for the entire project, using the `structlog` library for structured and configurable logging.
*   **Usage**: It is used to ensure consistent, informative, and machine-readable logs across all modules. The logger can be configured for different environments (e.g., development, production) and outputs (e.g., console, JSON).
*   **Key Information**:
    *   **`setup_logging()`**: A function to configure the global logging settings, including log level, file output, and format (JSON or console).
    *   **`get_logger()`**: A helper function to get a logger instance with the project's standardized configuration.
    *   **`LoggerContext`**: A context manager to log the start, completion, and failure of specific operations, automatically tracking duration and errors.
    *   **Specialized Loggers**: Includes functions like `log_data_info`, `log_model_metrics`, and `log_prediction` for logging specific, structured information related to data and model lifecycle events.

#### `src/utils/mlflow_analytics.py`

*   **Purpose**: This file contains a class to perform analytics on MLflow experiments using DuckDB.
*   **Usage**: It provides methods to query the MLflow database and extract useful information, such as model comparisons, experiment timelines, and best hyperparameters.
*   **Key Information**:
    *   **`MLflowAnalytics` class**: A class that encapsulates the analytics functionality.
    *   **`get_model_comparison()`**: Returns a DataFrame comparing all models across all metrics.
    *   **`get_experiment_timeline()`**: Returns a DataFrame showing the experiment timeline.
    *   **`find_best_hyperparameters()`**: Returns a DataFrame with the best hyperparameters for a specific model.

#### `src/utils/mlflow_duckdb_setup.py`

*   **Purpose**: This file contains classes to configure and set up MLflow with a DuckDB backend.
*   **Usage**: It provides a centralized way to initialize MLflow, manage experiments, and query experiment data using DuckDB.
*   **Key Information**:
    *   **`MLflowConfig` class**: A dataclass that encapsulates the MLflow configuration.
    *   **`MLflowDuckDBManager` class**: A class that manages MLflow operations with a DuckDB backend.
    *   **`setup_mlflow()`**: A method of `MLflowDuckDBManager` that initializes MLflow with the DuckDB backend, creates or gets an experiment, and sets the tracking URI.
    *   **`get_connection()`**: A method of `MLflowDuckDBManager` that returns a direct connection to the DuckDB database for analytics.
    *   **`query_experiments()`**: A method of `MLflowDuckDBManager` that executes a SQL query against the MLflow data using DuckDB.
    *   **`get_best_models()`**: A method of `MLflowDuckDBManager` that retrieves the best models based on a specified metric.
    *   **`analyze_experiments()`**: A method of `MLflowDuckDBManager` that performs a summary analysis of all experiments.
    *   **`create_mlflow_manager()`**: A factory function to create an `MLflowDuckDBManager` instance with configuration from environment variables.
    *   **`setup_mlflow_duckdb()`**: A convenience function to set up MLflow with a DuckDB backend using environment configuration.

## `tests/`

*   **Purpose**: This directory contains all the tests for the project.
*   **Usage**: For a detailed breakdown of the testing strategy, test suites, and how to run the tests, please see the [**`TESTING.md`**](./TESTING.md) file.

## `Makefile`

*   **Purpose**: This file provides a set of common command-line shortcuts for managing the project's lifecycle.
*   **Usage**: It allows developers to run complex or frequently used commands with a simple `make <target>` syntax.

## `configs/`

*   **Purpose**: This directory contains configuration files for the project.
*   **Key Files**:
    *   `logging_config.yaml`: Configures the logging for the project.

### `configs/logging_config.yaml`

*   **Purpose**: This file configures the logging for the project.
*   **Usage**: It is used by the `logging` module to configure the loggers, handlers, and formatters for the project.
*   **Key Information**:
    *   **`formatters`**: Defines different log formats, such as `default`, `json`, and `detailed`.
    *   **`handlers`**: Defines different log handlers, such as `console`, `file`, and `error_file`.
    *   **`loggers`**: Defines the loggers for different modules, such as `src`, `src.models`, and `src.data`.
    *   **`root`**: Defines the root logger.
