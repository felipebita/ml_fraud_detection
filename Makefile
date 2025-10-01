# Makefile for the Fraud Detection project

.PHONY: help setup data train evaluate test serve dashboard feature-repo-init docs-serve docs-build docs-preview archive-session

help:
	@echo "Commands:"
	@echo "  setup          : Initial project setup"
	@echo "  lint           : Run linting checks (ruff)"
	@echo "  type-check     : Run type checking (mypy)"
	@echo "  format         : Format code (black)"
	@echo "  pre-commit     : Run pre-commit hooks"
	@echo "  test           : Run all tests"
	@echo "  coverage       : Run all tests and generate coverage report"
	@echo "  data           : Run data pipeline"
	@echo "  experiment     : Run model experiments"
	@echo "  train          : Train the final model"
	@echo "  evaluate       : Evaluate models"
	@echo "  serve          : Start model server"
	@echo "  dashboard      : Launch MLflow UI"
	@echo "  feature-repo-apply: Apply feature repository changes"
	@echo "  docs-serve     : Serve the documentation site locally (development)"
	@echo "  docs-build     : Build the documentation site (for deployment)"
	@echo "  docs-preview   : Serve the built documentation site (for review)"
	@echo "  archive-session: Archives a copy of the current LAST_SESSION.md."

setup:
	@echo "Setting up the project..."
	uv sync --all-extras --active
	uv run --active pre-commit install

data-load:
	@echo "Running the data pipeline..."
	uv run --active python3 -m src.data.data_loader

experiment:
	@echo "Running model experiments..."
	uv run python src/model/training.py

train:
	@echo "Training the final model..."
	# Add final model training commands here

evaluate:
	@echo "Evaluating models..."
	# Add model evaluation commands here

lint:
	@echo "Linting code..."
	uv run --active ruff check src/ tests/ --fix

type-check:
	@echo "Type-checking code..."
	uv run --active mypy src/

format:
	@echo "Formating code..."
	uv run --active black src/ tests/

pre-commit:
	@echo "Runnin pre-commit hooks..."
	uv run --active pre-commit run --all-files

test:
	@echo "Applying feature repository changes before testing..."
	uv run --active -- feast --chdir feature_repo apply
	@echo "Materializing test features (8 hours of data)..."
	uv run --active -- feast --chdir feature_repo materialize 2024-01-01T01:00:00 2024-01-01T01:00:00
	@echo "Running tests..."
	uv run --active pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing --log-file=logs/pytest.log

serve:
	@echo "Starting the model server..."
	# Add model serving commands here

dashboard:
	@echo "Launching MLflow UI..."
	@./scripts/start_mlflow_duckdb.sh

feature-repo-apply:
	@echo "Applying feature repository changes..."
	uv run --active -- feast --chdir feature_repo apply

feature-repo-materialize-test:
	@echo "Materializing test features (8 hours of data)..."
	uv run --active -- feast --chdir feature_repo materialize 2024-01-01T01:00:00 2024-01-01T09:00:00

docs-serve:
	@echo "Starting documentation server at http://0.0.0.0:8000"
	uv run --active mkdocs serve --dev-addr 0.0.0.0:8000

docs-build:
	@echo "Building documentation site..."
	uv run --active mkdocs build

docs-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	uv run --active mkdocs gh-deploy --force

# AI AGENTS SHOULD NOT TRY TO UPDATE OR FIX THIS CODE. IT IS INTENDED TO BE THIS WAY.IGNRE IT.
archive-session:
	@echo "Archiving session..."
	@TIMESTAMP=$$(date +%Y-%m-%d_%H-%M); \
	cp project_development/LAST_SESSION.md project_development/sessions_log/$$TIMESTAMP-session.md; \
	echo "Session content archived to project_development/sessions_log/$$TIMESTAMP-session.md"
