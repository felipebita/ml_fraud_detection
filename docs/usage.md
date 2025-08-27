# Project Usage Guide

This guide provides a comprehensive overview of how to run, test, and manage this project. All commands are executed via `docker compose exec app <command>` and are simplified using the `Makefile`.

## Development Workflow

These commands are essential for day-to-day development, including managing the environment and ensuring code quality.

### Managing the Environment

The development environment is managed by Docker Compose.

-   **Start all services:**
    ```bash
    docker compose up --build -d
    ```
    *(The `--build` flag is only needed if you change dependencies in `pyproject.toml`)*

-   **Stop all services:**
    ```bash
    docker compose down
    ```

-   **View logs from all services:**
    ```bash
    docker compose logs -f
    ```

-   **Enter an interactive shell in the app container:**
    ```bash
    docker compose exec app bash
    ```

### Code Quality & Testing

-   **Run all tests with coverage:**
    ```bash
    docker compose exec app make test
    ```

-   **Format code with Black:**
    ```bash
    docker compose exec app make format
    ```

-   **Lint code with Ruff:**
    ```bash
    docker compose exec app make lint
    ```

-   **Run static type checking with MyPy:**
    ```bash
    docker compose exec app make type-check
    ```

## Machine Learning Workflow

These commands are used to execute the core ML pipeline steps.

-   **Run the data processing pipeline:**
    This command executes the data loading and validation scripts.
    ```bash
    docker compose exec app make data
    ```

-   **Train the model:**
    *(This target is not yet implemented)*
    ```bash
    docker compose exec app make train
    ```

-   **Evaluate the model:**
    *(This target is not yet implemented)*
    ```bash
    docker compose exec app make evaluate
    ```

-   **Access the MLflow UI:**
    The MLflow UI is available at [http://localhost:5000](http://localhost:5000) to track experiments.

## Documentation Workflow

-   **Serve the documentation site locally:**
    This command starts a live-reloading server for the documentation.
    ```bash
    docker compose exec app make docs-serve
    ```
    The site will be available at [http://localhost:8000](http://localhost:8000).

-   **Build the static documentation site:**
    This command generates the static HTML files for the documentation site into the `site/` directory.
    ```bash
    docker compose exec app make docs-build
    ```
