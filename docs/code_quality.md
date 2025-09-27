# Code Quality

This project enforces a high standard of code quality through a combination of automated tools. These tools are configured to run automatically before each commit, ensuring that all code in the repository is consistent, readable, and free of common errors.

## Pre-commit Hooks

The project uses [pre-commit](https://pre-commit.com/) to manage and maintain a set of Git hooks. These hooks are run automatically before each commit to inspect the code being committed. The configuration is stored in the `.pre-commit-config.yaml` file.

The following tools are configured to run as pre-commit hooks:

### `pre-commit-hooks`

*   **Purpose**: A collection of basic, essential hooks that perform checks on files.
*   **Key Hooks**:
    *   `trailing-whitespace`: Trims trailing whitespace.
    *   `end-of-file-fixer`: Ensures that a file is either empty or ends with a single newline.
    *   `check-yaml`: Checks yaml files for parseable syntax.
    *   `check-added-large-files`: Prevents giant files from being committed.
    *   `check-merge-conflict`: Checks for files that contain merge conflict strings.
    *   `detect-private-key`: Detects the presence of private keys.
    *   `check-ast`: Checks Python files for valid syntax.
    *   `check-docstring-first`: Checks that docstrings are the first statement in a module, class, or function.
    *   `debug-statements`: Checks for debugger imports and `breakpoint()` calls.

### `black`

*   **Purpose**: An opinionated code formatter for Python.
*   **Usage**: It automatically reformats Python code to ensure a consistent style across the project. This eliminates debates over code style and makes the code more readable.

### `ruff`

*   **Purpose**: An extremely fast Python linter, written in Rust.
*   **Usage**: It checks for a wide range of code errors, style issues, and potential bugs. The `--fix` argument allows it to automatically fix many of the issues it finds.

### `mypy`

*   **Purpose**: A static type checker for Python.
*   **Usage**: It analyzes the code to ensure that variables and functions are used with the correct types. This helps to catch type-related errors before the code is even run. The configuration is set to only check the `src/` directory.

### Synchronizing Pre-commit Environments

A key challenge in this project was ensuring consistent behavior of the pre-commit hooks across different environments. We discovered that the `pre-commit` hooks can run in two distinct contexts:

1.  **The Local `git commit` Hook:** When you run `git commit`, `pre-commit` creates and manages its own isolated Python environment to run the hooks. This environment is cached locally on your machine.
2.  **The Dockerized `make pre-commit` Command:** When you run `make pre-commit`, the hooks are executed inside the project's Docker container, using the `uv` environment defined in `pyproject.toml`.

These two environments were found to have different dependencies and package versions, which caused `mypy` to report conflicting errors. To solve this, we synchronized the environments by modifying the `.pre-commit-config.yaml` to ensure the `mypy` hook uses the same dependencies as the main project. This was achieved by explicitly listing the required type-stub packages in the `additional_dependencies` section of the `mypy` hook, ensuring consistent and predictable behavior everywhere.

## Usage

While the pre-commit hooks run automatically, you can also run the tools manually. This is useful if you want to check your code before committing, or if you want to apply formatting and linting to the entire codebase.

The following `make` commands are available:

*   `make format`: Formats the code with `black`.
*   `make lint`: Lints the code with `ruff` and automatically fixes issues.
*   `make type-check`: Runs the `mypy` static type checker.
*   `make pre-commit`: Runs all the pre-commit hooks on all files.

## Hosting the Documentation

The documentation for this project is built using [MkDocs](https://www.mkdocs.org/) and can be hosted for free on [GitHub Pages](https://pages.github.com/).

There are two ways to deploy the documentation to GitHub Pages:

### 1. Using `mkdocs gh-deploy`

This is the recommended method, as it is the simplest.

**Prerequisites:**

*   You need to have a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with the `repo` scope.

**Steps:**

1.  Make sure the `repo_url` in `mkdocs.yml` is set to your repository's URL.
2.  Run the following command:

    ```bash
    docker compose exec app make docs-deploy
    ```

    When prompted for your username and password, enter your GitHub username and use your personal access token as the password.

3.  After the command has finished, go to your repository's settings on GitHub, navigate to the "Pages" section, and select the `gh-pages` branch as the source for your GitHub Pages site.

### 2. Manual Deployment

If the `mkdocs gh-deploy` command does not work, you can deploy the documentation manually.

**Steps:**

1.  Build the documentation:

    ```bash
    docker compose exec app make docs-build
    ```

2.  Navigate into the `site` directory:

    ```bash
    cd site
    ```

3.  Initialize a new git repository and commit the files:

    ```bash
    git init
    git checkout -b gh-pages
    git add .
    git commit -m "Deploy documentation"
    ```

4.  Add your repository as the remote origin and push the `gh-pages` branch:

    ```bash
    git remote add origin <your-repository-url>
    git push -f origin gh-pages
    ```

5.  After the command has finished, go to your repository's settings on GitHub, navigate to the "Pages" section, and select the `gh-pages` branch as the source for your GitHub Pages site.

## Continuous Integration & Deployment

The project uses GitHub Actions for Continuous Integration and Continuous Deployment (CI/CD). The workflows are defined in the `.github/workflows` directory.

### CI Workflow (`ci.yml`)

The `ci.yml` workflow runs on every push and pull request to the `main` branch. It ensures the quality and correctness of the code by running the following jobs:

1.  **Build Docker services**: It builds the `app` Docker service to ensure the development environment is correctly configured.
2.  **Run pre-commit checks**: It executes `make pre-commit` to run all the pre-commit hooks, which include checks for formatting (`black`), linting (`ruff`), and static typing (`mypy`).
3.  **Run tests**: It executes `make test` to run the entire test suite with `pytest`.

This workflow guarantees that any code merged into the `main` branch adheres to the project's quality standards and passes all tests.

### Documentation Deployment Workflow (`docs.yml`)

The `docs.yml` workflow automates the deployment of the project documentation to GitHub Pages. It is triggered on every push to the `main` branch that includes changes in the `docs/` directory or the `mkdocs.yml` file.

The workflow performs the following steps:

1.  **Checkout code**: Checks out the repository.
2.  **Setup Python and uv**: Sets up the Python environment and the `uv` package manager.
3.  **Install dependencies**: Installs the project dependencies, including `mkdocs`.
4.  **Build docs**: Builds the documentation site using `uv run mkdocs build`.
5.  **Deploy to GitHub Pages**: Deploys the generated `site/` directory to the `gh-pages` branch, making it available as a static website.
