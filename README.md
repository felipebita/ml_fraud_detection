# Real-Time Fraud Detection API

[![CI/CD Status](https://github.com/felipebita/ml_fraud_detection/actions/workflows/ci.yml/badge.svg)](https://github.com/felipebita/ml_fraud_detection/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/felipebita/ml_fraud_detection/branch/main/graph/badge.svg)](https://codecov.io/gh/felipebita/ml_fraud_detection)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides a production-ready machine learning system to power a real-time fraud detection API. It is designed to classify mobile financial transactions as fraudulent or legitimate, with a focus on MLOps best practices.

## Documentation

This project is extensively documented to guide you through its architecture, usage, and development processes. For a comprehensive understanding, please visit the [**full documentation site**](https://felipebita.github.io/ml_fraud_detection/).

Key sections of the documentation include:

-   **[Usage Guide](docs/usage.md):** Detailed instructions on how to set up the development environment, run the ML pipeline, use the feature store, and execute code quality checks. This is the best place to start.
-   **[Business Context](docs/business.md):** An overview of the business problem, the monetization model, and the project's goals.
-   **[Project Files](docs/project_files.md):** A complete reference for every significant file and directory in the project, explaining its purpose and usage.
-   **[Testing Strategy](docs/testing.md):** A guide to the project's testing philosophy, including how to run tests and understand the different types of tests.
-   **[Code Quality](docs/code_quality.md):** Information on the tools and standards used to maintain high code quality, including linting, formatting, and type checking.
-   **[Logging](docs/logging.md):** An explanation of the structured logging system used throughout the project.

You can also serve the documentation locally by running `docker compose exec app make docs-serve` and navigating to [http://localhost:8000](http://localhost:8000).

## Project Structure

The project is organized into the following key directories:

-   `src/`: Main source code for the application.
-   `data/`: Data files, organized into `raw`, `processed`, and `reports`.
-   `configs/`: Configuration files for the application and logging.
-   `tests/`: Unit and integration tests.
-   `docs/`: Project documentation.
-   `feature_repo/`: Feast feature store definitions.

For a detailed explanation of each file and directory, please see the [**Project File Documentation**](./docs/project_files.md).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
