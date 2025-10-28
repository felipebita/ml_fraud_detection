# Project Usage Guide

This guide provides a comprehensive overview of how to run, test, and manage this project.

## Local Development Setup

To ensure consistency between your local development environment and the containerized environment used for CI/CD, it is crucial to use the same versions of dev dependencies, including `pre-commit` and its hooks. This project uses `uv` to manage dependencies and `uv.lock` as the single source of truth for pinned versions.

Follow these steps to set up your local environment:

### 1. Install `uv`

If you don't have `uv` installed on your local machine, you can install it by following the official instructions: [https://github.com/astral-sh/uv#installation](https://github.com/astral-sh/uv#installation)

### 2. Create and Sync your Virtual Environment

1.  Create a virtual environment in the project's root directory:
    ```bash
    python3 -m venv .venv
    ```

2.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

3.  Sync your environment with the locked dependencies:
    ```bash
    uv sync --extra dev
    ```
    This command will install the exact versions of all development dependencies specified in the `uv.lock` file, which are needed to run the pre-commit hooks.

### 3. Install Pre-commit Hooks

Now that you have the correct version of `pre-commit` installed in your virtual environment, you can install the Git hooks:

```bash
pre-commit install
```

By following these steps, you ensure that the pre-commit hooks running on your local machine use the same library versions as the CI pipeline, preventing any discrepancies.

## Container Environment Setup

### 1. SSH Agent Configuration

Before starting the services for the first time, you must ensure your SSH agent is running and configured correctly on your host machine. This is required for the Docker container to access your local SSH keys securely, which is necessary for operations like interacting with private Git repositories and allowing MLflow to track experiment commits.

If your SSH agent is not configured, you will see this warning when running `docker compose up`:

```
WARN[0000] The "SSH_AUTH_SOCK" variable is not set. Defaulting to a blank string.
```

To fix this, run the following commands in your terminal before running `docker compose up`:

1.  **Start the ssh-agent:**
    ```bash
    eval "$(ssh-agent -s)"
    ```

2.  **Add your SSH key:**
    ```bash
    ssh-add
    ```

#### Automating `ssh-agent` on Shell Startup

To avoid running the manual commands every time you open a new terminal, you can add a script to your shell's startup file (e.g., `~/.bashrc` or `~/.zshrc`).

The following script is a robust way to manage your `ssh-agent`. It checks if the agent is running and accessible, and if not, it starts a new one. This avoids issues with stale agent information after a system reboot.

Add the following code to the end of your `~/.bashrc` or `~/.zshrc` file:

```bash
# ssh-agent configuration
if [ -f ~/.ssh-agent-info ]; then
    . ~/.ssh-agent-info
fi

# Check if the agent is running and accessible
if ! ssh-add -l >/dev/null 2>&1; then
    # If not, start a new agent
    ssh-agent -s | grep -v echo > ~/.ssh-agent-info
    . ~/.ssh-agent-info
    ssh-add
fi
```

After adding the script, you'll need to restart your terminal or run `source ~/.bashrc` (or `source ~/.zshrc`) to apply the changes.

### 2. Environment Setup

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

-   **Update the environment without rebuilding:**
    If you have updated the `pyproject.toml` file with new dependencies, you can update the environment inside the container without rebuilding it by running:
    ```bash
    docker compose exec app make setup
    ```

### 3. Initial Data Setup

-   **Download and prepare the initial raw dataset:**
    ```bash
    docker compose exec app make data-setup
    ```

## Application Usage

### Machine Learning Workflow

These commands are used to execute the core ML pipeline steps and the configuration parameters can be found in `configs/config.yaml`.

-   **Run the data loading pipeline:**
    ```bash
    docker compose exec app make data-load
    ```

-   **Run the data splitting pipeline:**
    ```bash
    docker compose exec app make data-split
    ```

-   **Run the entire data pipeline (load and split):**
    ```bash
    docker compose exec app make data
    ```

-   **Run a quick model comparison experiment:**
    This command runs a quick experiment to compare the performance of multiple models with their default hyperparameters.
    ```bash
    docker compose exec app make quick-experiment
    ```

-   **Run a hyperparameter grid search experiment:**
    This command runs a grid search experiment for a single model to find the best hyperparameter combination.
    ```bash
    docker compose exec app make gs-experiment
    ```

-   **Train the final model:**
    ```bash
    docker compose exec app make train
    ```

-   **Access the MLflow UI:**
    The MLflow UI is available at [http://localhost:5000](http://localhost:5000) to track experiments.

### Feature Store Workflow

-   **Apply feature store changes:**
    This command applies the changes from your feature definitions to the feature store.
    ```bash
    docker compose exec app make feature-repo-apply

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

-   **Run pre-commit hooks:**
    ```bash
    docker compose exec app make pre-commit
    ```

### Documentation Workflow

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

-   **Deploy the documentation to GitHub Pages:**
    ```bash
    docker compose exec app make docs-deploy
    ```

### Session Archiving

-   **Archive the current session:**
    This command archives a copy of the current `LAST_SESSION.md` file.
    ```bash
    docker compose exec app make archive-session
    ```
