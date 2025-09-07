# Project Usage Guide

This guide provides a comprehensive overview of how to run, test, and manage this project. All commands are executed via `docker compose exec app <command>` and are simplified using the `Makefile`.

## Initial Setup: SSH Agent Configuration

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

### Automating `ssh-agent` on Shell Startup

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

## Feature Store Workflow

-   **Apply feature store changes:**
    This command applies the changes from your feature definitions to the feature store.
    ```bash
    docker compose exec app make feature-repo-apply
    ```

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
