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

## Basic Usage

All commands should be run inside the `app` container using `docker compose exec app <command>`. A `Makefile` provides shortcuts for common tasks.

-   **Run all tests:**
    ```bash
    docker compose exec app make test
    ```
-   **Format and lint code:**
    ```bash
    docker compose exec app make format
    ```
-   **Run the data pipeline:**
    ```bash
    docker compose exec app make data
    ```
-   **See all available commands:**
    ```bash
    docker compose exec app make help
    ```

### Accessing Services

-   **MLflow UI:** [http://localhost:5000](http://localhost:5000)
-   **Documentation Site (Local):** Run `docker compose exec app make docs-serve` and go to [http://localhost:8000](http://localhost:8000)

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for details on how to submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
