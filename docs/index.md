# Real-Time Fraud Detection API

[![CI/CD Status](https://github.com/felipebita/ml_fraud_detection/actions/workflows/ci.yml/badge.svg)](https://github.com/felipebita/ml_fraud_detection/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/felipebita/ml_fraud_detection/branch/main/graph/badge.svg)](https://codecov.io/gh/felipebita/ml_fraud_detection)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides a production-ready machine learning system to power a real-time fraud detection API. The model classifies mobile financial transactions as fraudulent or legitimate, with a primary focus on optimizing for financial performance and demonstrating MLOps best practices.

## 1. Business Context

"Blocker Fraud Systems" is a B2B SaaS company providing a fraud detection API to e-commerce and fintech clients. The service is designed to reduce clients' fraud-related losses while protecting their customer experience by minimizing the rejection of legitimate transactions. The service operates on a hybrid pricing model, combining a base API fee with a performance incentive based on the value of correctly identified fraud.

## 2. Project Goals

The central goal is to develop a machine learning model that maximizes revenue under the defined business model. This involves:
- Developing a predictive model for fraud risk.
- Optimizing the classification threshold for profitability.
- Quantifying the financial impact for both the client and the company.

## 3. Installation

This project uses Docker and Docker Compose to create a consistent and isolated development environment.

**Prerequisites:**
- Docker
- Docker Compose

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/felipebita/ml_fraud_detection.git
    cd ml_fraud_detection
    ```

2.  **Configure Environment Variables:**
    Copy the example environment file. The default values are suitable for local development.
    ```bash
    cp .env.example .env
    ```
    *Note: Your local user ID and group ID will be passed to the container to prevent file permission issues. The defaults are `1000:1000`.*

3.  **Build and Start the Services:**
    This command will build the Docker images and start the `app` and `mlflow` services in the background.
    ```bash
    docker-compose up --build -d
    ```

## 4. Project Usage

### Managing the Environment

-   **Starting the environment:** After the initial build, you can start all services in the background with:
    ```bash
    docker-compose up -d
    ```

-   **Stopping the environment:** To stop and remove the containers for a clean shutdown, use:
    ```bash
    docker-compose down
    ```

-   **Checking logs:** To view the real-time logs from all running services, you can use:
    ```bash
    docker-compose logs -f
    ```

### Running Commands

All development commands should be run inside the `app` container to ensure consistency. This is done by prefixing your commands with `docker-compose exec app`.

This project uses a `Makefile` to simplify common commands.

-   **Run all tests:**
    ```bash
    docker-compose exec app make test
    ```
-   **Format and lint the code:**
    ```bash
    docker-compose exec app make format
    docker-compose exec app make lint
    ```
-   **Run the data pipeline:**
    ```bash
    docker-compose exec app make data
    ```
-   **Access the MLflow UI:**
    The MLflow UI is available at [http://localhost:5000](http://localhost:5000) in your browser.

For a full list of commands, run `docker-compose exec app make help`.

## 5. Project Structure

The repository is organized to support a scalable, production-focused MLOps workflow.

```
├── configs/            # Configuration files (logging, parameters).
├── data/               # Raw, processed, and feature data.
├── docs/               # High-level documentation (testing strategy, architecture).
├── models/             # Serialized models and artifacts.
├── notebooks/          # Jupyter notebooks for EDA and analysis.
├── scripts/            # Standalone scripts for tasks like starting services.
├── src/                # Main source code for the project.
│   ├── data/           # Data loading, validation, and processing.
│   ├── features/       # Feature engineering and transformation.
│   ├── models/         # Model training and prediction logic.
│   └── utils/          # Utility functions (logging, config management).
├── tests/              # Unit and integration tests.
├── .github/            # CI/CD workflows.
├── Makefile            # Command shortcuts for development tasks.
├── mkdocs.yml          # Configuration for the documentation site.
├── pyproject.toml      # Project metadata and dependencies.
└── README.md           # This file.
```

## 6. Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for details on how to submit a pull request.

## 7. License

This project is licensed under the MIT License. See the `LICENSE` file for details.
