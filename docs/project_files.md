# Project File Documentation

This file provides a comprehensive overview of all files in the project, including their purpose, usage, and any other relevant information.

## Files

- `./.github/`
    - `./.github/workflows/ci.yml`
    - `./.github/workflows/docs.yml`
- `./configs/`
    - `./configs/config.yaml`
    - `./configs/logging_config.yaml`
- `./data/`
    - `./data/download/`
        - `./data/download/complete_synthetic_financial_dataset.csv`
    - `./data/features/`
    - `./data/processed/`
        - `./data/processed/processed_transactions.parquet`
    - `./data/raw/`
        - `./data/raw/fraud_data.csv`
    - `./data/reports/`
        - `./data/reports/processed_data_profile.json`
        - `./data/reports/raw_data_profile.json`
- `./docs/`
    - `./docs/business.md`
    - `./docs/project_files.md`
- `./feature_repo/`
    - `./definitions.py`
    - `./feature_store.yaml`
    - `./feature_repo/data/`
        - `./feature_repo/data/online_store.db`
        - `./feature_repo/data/registry.db`
- `./dhtmlcov/`
- `./logs/`
    - `./logs/fraud_detection.log`
    - `./logs/pytest.log`
- `./models/`
- `./notebooks/`
    - `./notebooks/01_eda.ipynb`
- `./scripts/`
    - `./scripts/create_dummy_data.py`
    - `./scripts/get_timestamp_range.py`
    - `./scripts/test_mlflow_setup.py`
    - `./scripts/test_profiler.py`
- `./src/`
    - `./src/__init__.py`
    - `./src/data/`
        - `./src/data/data_loader.py`
        - `./src/data/data_profiler.py`
        - `./src/data/data_validator.py`
    - `./src/utils/`
        - `./src/utils/config.py`
        - `./src/utils/logger.py`
        - `./src/utils/mlflow_analytics.py`
        - `./src/utils/mlflow_duckdb_setup.py`
- `./tests/`
    - `./tests/conftest.py`
    - `./tests/integration`
        - `./tests/integration/test_feast_basic.py`
    - `./tests/unit/`
        - `./tests/unit/test_data_loader.py`
        - `./tests/unit/test_data_profiler.py`
        - `./tests/unit/test_data_validator.py`
        - `./tests/unit/test_mlflow_analytics.py`
        - `./tests/unit/test_duckdb_setup.py`
- `./.env`
- `./.env.example`
- `./.gitignore`
- `./.pre-commit-config.yaml`
- `./coverage.xml`
- `./docker-compose.yml`
- `./Dockerfile`
- `./Makefile`
- `./mkdocs.yml`
- `./mlflow.duckdb`
- `./pyproject.toml`
- `./README.md`
- `./uv.lock`

## `.github/`

This directory contains all the GitHub Actions workflows for the project.

### `.github/workflows/ci.yml`

*   **Purpose**: This workflow defines the Continuous Integration (CI) pipeline for the project.
*   **Usage**: It is triggered on every push and pull request to the `main` branch. It runs a series of checks to ensure code quality and correctness, including linting, type checking, and running the test suite.

### `.github/workflows/docs.yml`

*   **Purpose**: This workflow automates the deployment of the project documentation to GitHub Pages.
*   **Usage**: It is triggered on every push to the `main` branch that includes changes in the `docs/` directory or the `mkdocs.yml` file. It builds the documentation and deploys it to the `gh-pages` branch.


## `data/`

*   **Purpose**: This directory contains the data for the project.
*   **Key Directories**:
    *   `raw`: Contains the raw data.
    *   `processed`: Contains the processed data.
    *   `features`: Contains the engineered features.

### `data/download/complete_synthetic_financial_dataset.csv`

*   **Purpose**: The original, unmodified source data for the project, downloaded from Kaggle.
*   **Usage**: It serves as the input for the data ingestion pipeline (`src/data/data_loader.py`) and should be treated as immutable.

### `data/raw/`

*   **Purpose**: This directory contains the raw, immutable data for the project.
*   **Usage**: Data in this directory should be treated as read-only. No modifications should be made to the files in this directory.

#### `data/raw/fraud_data.csv`

*   **Purpose**: The original, unmodified source data for the project.
*   **Usage**: It serves as the input for the data ingestion pipeline (`src/data/data_loader.py`) and should be treated as immutable.
*   **Key Information**: Contains raw transaction records, which may include inconsistencies or errors that the pipeline is designed to handle.

### `data/processed/`

*   **Purpose**: This directory contains the processed and cleaned data.
*   **Usage**: The data in this directory is the result of cleaning and preprocessing the raw data. It is the input for the feature engineering step.

#### `data/processed/processed_transactions.parquet`

*   **Purpose**: The cleaned, validated, and standardized dataset.
*   **Usage**: It is the primary output of the data ingestion pipeline and serves as the trusted source of truth for all downstream tasks, including feature engineering and model training.
*   **Key Information**: Stored in Parquet format for efficiency. All records have been validated against the Pandera schema in `src/data/data_validator.py`.

### `data/reports/`

*   **Purpose**: This directory contains all data-related reports generated by the pipeline.
*   **Usage**: It stores data quality and profiling reports, providing insights into the data at various stages. These reports are artifacts that help in monitoring data quality over time.

#### `data/reports/raw_data_profile.json`

*   **Purpose**: A detailed JSON report containing a statistical and structural profile of the raw data, generated immediately after loading from the source CSV.
*   **Usage**: Used to understand the quality and characteristics of the incoming source data before any validation or cleaning. Essential for diagnosing issues with the source data feed.
*   **Key Information**: Generated automatically by the `data_loader.py` script.

#### `data/reports/processed_data_profile.json`

*   **Purpose**: A detailed JSON report containing a statistical and structural profile of the processed data.
*   **Usage**: Used to understand the quality and characteristics of the final, cleaned data that will be used for feature engineering. It provides a snapshot of the data that the model will ultimately learn from.
*   **Key Information**: Generated automatically by the `data_loader.py` script after the `DataValidator` has run. Comparing this to the raw profile shows the effect of the cleaning/validation steps.

### `data/features/`

*   **Purpose**: This directory contains the engineered features.
*   **Usage**: The data in this directory is the result of the feature engineering process. It is the input for the model training.

## `feature_repo/`

*   **Purpose**: This directory contains all the definitions and configurations for the Feast feature repository.

### `feature_repo/feature_store.yaml`

*   **Purpose**: The main configuration file for the feature store.
*   **Usage**: It defines the project name, registry path, provider (local), and online store configuration.

### `feature_repo/definitions.py`

*   **Purpose**: This file contains the Python-based definitions for all features.
*   **Usage**: It defines the entities, feature views, and feature services that comprise the feature store.

### `feature_repo/data/`

*   **Purpose**: This directory holds the local data files generated by Feast for the local development environment.

#### `feature_repo/data/online_store.db`

*   **Purpose**: This is the SQLite database file that acts as the online store during local development.
*   **Usage**: It stores features that have been materialized from the offline store, providing low-latency access for serving.

#### `feature_repo/data/registry.db`

*   **Purpose**: This is the SQLite database that stores the feature registry.
*   **Usage**: It keeps track of all the registered feature definitions, entities, and their metadata.

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

### `scripts/create_dummy_data.py`

*   **Purpose**: This script creates a small, version-controlled dummy dataset for use in CI/CD pipelines.
*   **Usage**: It is run during the CI workflow to generate a minimal dataset for tests, avoiding the need to store the full dataset in the repository.

### `scripts/get_timestamp_range.py`

*   **Purpose**: An auxiliary script to get the minimum and maximum timestamp from the processed data.
*   **Usage**: It is used to determine the time range of the data in the processed Parquet file, which can be useful for setting `materialize` windows.

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

*   **Purpose**: This script is responsible for loading the raw data from its source.
*   **Usage**: It is used to load the raw data from a CSV file into a pandas DataFrame. It does not perform any validation itself.
*   **Key Information**:
    *   **`load_data()`**: Loads transaction data from a CSV file and returns a raw DataFrame.

### `src/data/data_validator.py`

*   **Purpose**: This script contains the `DataValidator` class, which is the single source of truth for data validation.
*   **Usage**: It uses a comprehensive Pandera schema to validate the entire DataFrame at once, checking data types, value ranges, and structural integrity.
*   **Key Information**:
    *   It uses the `pandera` library to define and execute all data validation rules.
    *   It is the primary mechanism for ensuring data quality after loading.

### `src/data/data_profiler.py`

*   **Purpose**: This script profiles the data to provide a comprehensive overview of the data quality and characteristics.
*   **Usage**: It is used to generate a data profile report that includes basic information, data types, missing values, numerical and categorical stats, data quality issues, class distribution, and temporal analysis.
*   **Key Information**:
    *   **`DataProfiler` class**: A class that encapsulates the data profiling functionality.
    *   **`generate_profile()`**: Generates a comprehensive data profile.
    *   **`export_profile()`**: Exports the profile to a JSON file.
    *   **`get_summary_report()`**: Generates a human-readable summary report.

### `src/utils/`

#### `src/utils/config.py`

*   **Purpose**: A utility module that provides a centralized system for managing project configuration.
*   **Usage**: It exposes a single function, `get_config()`, which loads settings from `configs/config.yaml` and `configs/logging_config.yaml`, merges them, and overrides them with any matching environment variables. This provides a single, reliable source of truth for all configuration parameters throughout the application.

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
    *   **`get_best_models()`**: A method of `MLflowDuckDBManager` that retrieves the best models whbased on a specified metric.
    *   **`analyze_experiments()`**: A method of `MLflowDuckDBManager` that performs a summary analysis of all experiments.
    *   **`create_mlflow_manager()`**: A factory function to create an `MLflowDuckDBManager` instance with configuration from environment variables.
    *   **`setup_mlflow_duckdb()`**: A convenience function to set up MLflow with a DuckDB backend using environment configuration.

## `tests/`

*   **Purpose**: This directory contains all the tests for the project.
*   **Usage**: For a detailed breakdown of the testing strategy, test suites, and how to run the tests, please see the [**`testing.md`**](./testing.md) file.

## `Makefile`

*   **Purpose**: This file provides a set of common command-line shortcuts for managing the project's lifecycle.
*   **Usage**: It allows developers to run complex or frequently used commands with a simple `make <target>` syntax.

## `configs/`

*   **Purpose**: This directory contains configuration files for the project.
*   **Key Files**:
    *   `config.yaml`: The primary configuration file for the project. It stores non-sensitive settings such as file paths, model parameters, and environment-specific settings. This file is loaded by `src/utils/config.py` and its values can be overridden by environment variables.
    *   `logging_config.yaml`: Configures the logging for the project.

### `configs/logging_config.yaml`

*   **Purpose**: This file configures the logging for the project.
*   **Usage**: It is used by the `logging` module to configure the loggers, handlers, and formatters for the project.
*   **Key Information**:
    *   **`formatters`**: Defines different log formats, such as `default`, `json`, and `detailed`.
    *   **`handlers`**: Defines different log handlers, such as `console`, `file`, and `error_file`.
    *   **`loggers`**: Defines the loggers for different modules, such as `src`, `src.models`, and `src.data`.
    *   **`root`**: Defines the root logger.

## `Dockerfile`

*   **Purpose**: This file defines the Docker image for the application, ensuring a consistent and reproducible environment for development and deployment.
*   **Usage**: It is used by `docker-compose` to build the images for the `app` and `mlflow` services.
*   **Key Information**:
    *   **Base Image**: Uses the `python:3.11-slim` image as a lightweight base.
    *   **Working Directory**: Sets the working directory to `/app`.
    *   **Dependency Management**: Copies the `pyproject.toml` and `uv.lock` files and uses `uv` to install all project dependencies, including optional extras.
    *   **Git Installation**: Installs `git` to prevent warnings from MLflow about being unable to track Git commits.
    *   **Application Code**: Copies the entire project directory into the image.

## `docker-compose.yml`

*   **Purpose**: This file defines and configures the multi-container Docker application for a local development environment.
*   **Usage**: It is used with the `docker-compose` command to start, stop, and manage the application services (`docker-compose up`, `docker-compose down`).
*   **Key Information**:
    *   **`app` Service**:
        *   The main container for running the application code and scripts.
        *   Builds its image using the `Dockerfile` in the root directory.
        *   Mounts the current project directory into the container at `/app` to allow for live code changes without rebuilding the image.
        *   Depends on the `mlflow` service to ensure the tracking server is available.
        *   The `command: tail -f /dev/null` is used to keep the container running during development, allowing for interactive use with `docker compose exec`.
    *   **`mlflow` Service**:
        *   Runs the MLflow tracking server.
        *   Exposes port `5000` to allow access to the MLflow UI from the host machine.
        *   Uses volumes to persist MLflow data (`mlruns` directory for artifacts and `mlflow.duckdb` for the database) on the host machine.
        *   The command starts the MLflow server using `uv run`, configured with a DuckDB backend and the appropriate artifact root.
