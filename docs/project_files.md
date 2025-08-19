# Project File Documentation

This file provides a comprehensive overview of all files in the project, including their purpose, usage, and any other relevant information.

## Files

- `./.github/`
- `./configs/`
- `./data/`
- `./docs/`
- `./models/`
- `./notebooks/`
- `./scripts/`
- `./src/`
- `./tests/`
- `./.gitignore`
- `./.pre-commit-config.yaml`
- `./Makefile`
- `./PROJECT_PLAN.md`
- `./pyproject.toml`
- `./README.md`
- `./TESTING.md`
- `./uv.lock`


## `.gitignore`

*   **Purpose**: This file specifies intentionally untracked files that Git should ignore.
*   **Usage**: It's used to avoid committing files that are not necessary for the project, such as environment variables, large data files, and model experiment files.

## `.pre-commit-config.yaml`

*   **Purpose**: This file configures the pre-commit hooks that are run before each commit to ensure code quality and consistency.
*   **Usage**: It helps to automate code formatting, linting, and other checks to catch issues before they are committed to the repository.

## `pyproject.toml`

*   **Purpose**: This file is the unified configuration file for the project, specifying metadata, dependencies, and tool settings.
*   **Usage**: It is used by `pip` and other tools to manage the project's packaging, dependencies, and development environment.

## `README.md`

*   **Purpose**: This file provides a high-level overview of the project, including the business context, project goals, and scope of analysis.
*   **Usage**: It is the first file that users see when they visit the project's repository, so it should contain essential information about the project.

## `uv.lock`

*   **Purpose**: This file is the lock file for the `uv` package manager. It records the exact versions of all dependencies used in the project.
*   **Usage**: It ensures that the project has a reproducible environment by locking the versions of all dependencies, which prevents unexpected changes from new releases.

## `scripts/`

*   **Purpose**: This directory contains standalone scripts for various tasks, such as starting services or running tests.
*   **Key Files**:
    *   `start_mlflow_duckdb.sh`: Starts the MLflow tracking server with a DuckDB backend.
    *   `test_mlflow_setup.py`: A simple script to test the MLflow setup.

## `notebooks/`

*   **Purpose**: This directory contains Jupyter notebooks for exploratory data analysis (EDA), model analysis, and experimentation.

## `src/`

*   **Purpose**: This is the main source code directory for the project.

### `src/data/`

*   **`data_loader.py`**: Loads raw data from a CSV file and performs initial validation using Pydantic.
*   **`data_validator.py`**: Performs DataFrame-level validation using Pandera to ensure data quality and integrity.

### `src/utils/`

*   **`logger.py`**: Configures the centralized logging setup for the project.
*   **`mlflow_analytics.py`**: Provides tools for analyzing MLflow experiment data.
*   **`mlflow_duckdb_setup.py`**: Manages the setup and configuration of MLflow with a DuckDB backend.

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
