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

To set up the project, you need Python 3.11+ and `uv`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/felipebita/ml_fraud_detection.git
    cd your-repo
    ```

2.  **Create the virtual environment and install dependencies:**
    ```bash
    uv venv
    uv pip install -e .[dev,notebook]
    ```

3.  **Set up pre-commit hooks:**
    ```bash
    pre-commit install
    ```

4.  **Configure Environment Variables:**
    Copy the example environment file and fill in your details.
    ```bash
    cp .env.example .env
    ```

## 4. Quick Start

This project uses a `Makefile` to simplify common commands.

-   **Run all tests:**
    ```bash
    make test
    ```
-   **Format and lint the code:**
    ```bash
    make format
    make lint
    ```
-   **Start the MLflow UI:**
    ```bash
    make dashboard
    ```
-   **Run the training pipeline:**
    ```bash
    make train
    ```

For a full list of commands, run `make help`.

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
