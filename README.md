# Real-Time Fraud Detection API

[![CI/CD Status](https://github.com/felipebita/ml_fraud_detection/actions/workflows/ci.yml/badge.svg)](https://github.com/felipebita/ml_fraud_detection/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/felipebita/ml_fraud_detection/branch/main/graph/badge.svg)](https://codecov.io/gh/felipebita/ml_fraud_detection)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides a production-ready machine learning system to power a real-time fraud detection API. It is designed to classify mobile financial transactions as fraudulent or legitimate, with a focus on MLOps best practices.

## Documentation

For detailed information on project architecture, business context, and operational guides, please see the [**full documentation site**](https://felipebita.github.io/ml_fraud_detection/).

## Getting Started

This project uses Docker and Docker Compose to create a consistent and isolated development environment.

### Prerequisites

- Docker
- Docker Compose

### 1. Clone & Configure

```bash
# Clone the repository
git clone https://github.com/felipebita/ml_fraud_detection.git
cd ml_fraud_detection

# Copy the example environment file (defaults are fine for local use)
cp .env.example .env
```
*Note: Your local user ID and group ID are passed to the container to prevent file permission issues.*

### 2. Build & Run

This command builds the Docker images and starts the `app` and `mlflow` services in the background.

```bash
docker compose up --build -d
```
*The `--build` flag is only needed when dependencies in `pyproject.toml` change.*

### 3. Local Environment Setup (Optional)

If you want to run pre-commit hooks locally to ensure code quality before committing, you can set up a local virtual environment:

1.  **Install `uv`:** Follow the official instructions at [https://github.com/astral-sh/uv#installation](https://github.com/astral-sh/uv#installation).
2.  **Create and sync your virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    uv sync --extra dev
    ```
3.  **Install pre-commit hooks:**
    ```bash
    pre-commit install
    ```

## Usage

### Running Commands

All commands should be run inside the `app` container using `docker compose exec app <command>`. A `Makefile` provides shortcuts for common tasks.

-   **See all available commands:**
    ```bash
    docker compose exec app make help
    ```

### Code Quality

-   **Run all tests with coverage:**
    ```bash
    docker compose exec app make test
    ```
-   **Format code:**
    ```bash
    docker compose exec app make format
    ```
-   **Lint code:**
    ```bash
    docker compose exec app make lint
    ```
-   **Run static type checking:**
    ```bash
    docker compose exec app make type-check
    ```

### Machine Learning Workflow

-   **Run the data pipeline:**
    ```bash
    docker compose exec app make data
    ```
-   **Run a quick model experiment:**
    ```bash
    docker compose exec app make quick-experiment
    ```
-   **Run a grid search experiment:**
    ```bash
    docker compose exec app make gs-experiment
    ```
-   **Train the final model:**
    ```bash
    docker compose exec app make train
    ```

### Accessing Services

-   **MLflow UI:** [http://localhost:5000](http://localhost:5000)
-   **Documentation Site (Local):** Run `docker compose exec app make docs-serve` and go to [http://localhost:8000](http://localhost:8000)

## Project Structure

The project is organized into the following key directories:

-   `src/`: Main source code for the application.
-   `data/`: Data files, organized into `raw`, `processed`, and `reports`.
-   `configs/`: Configuration files for the application and logging.
-   `tests/`: Unit and integration tests.
-   `docs/`: Project documentation.
-   `feature_repo/`: Feast feature store definitions.

For a detailed explanation of each file and directory, please see the [**Project File Documentation**](./docs/project_files.md).

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for details on how to submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
