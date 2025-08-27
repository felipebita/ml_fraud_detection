# Makefile for the Fraud Detection project

.PHONY: help setup data train evaluate test serve dashboard feature-repo-init docs-serve docs-build docs-preview

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
	@echo "  train          : Train models"
	@echo "  evaluate       : Evaluate models"
	@echo "  serve          : Start model server"
	@echo "  dashboard      : Launch MLflow UI"
	@echo "  feature-repo-init: Initialize Feast feature repository"
	@echo "  docs-serve     : Serve the documentation site locally (development)"
	@echo "  docs-build     : Build the documentation site (for deployment)"
	@echo "  docs-preview   : Serve the built documentation site (for review)"

setup:
	@echo "Setting up the project..."
	uv sync --all-extras
	uv run pre-commit install

data:
	@echo "Running the data pipeline..."
	uv run python3 -m src.data.data_loader

train:
	@echo "Training models..."
	# Add model training commands here

evaluate:
	@echo "Evaluating models..."
	# Add model evaluation commands here

lint:
	@echo "Linting code..."
	uv run ruff check src/ tests/ --fix

type-check:
	@echo "Type-checking code..."
	uv run mypy src/

format:
	@echo "Formating code..."
	uv run black src/ tests/

pre-commit:
	@echo "Runnin pre-commit hooks..."
	uv run pre-commit run --all-files

test:
	@echo "Running tests..."
	uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

serve:
	@echo "Starting the model server..."
	# Add model serving commands here

dashboard:
	@echo "Launching MLflow UI..."
	@./scripts/start_mlflow_duckdb.sh

feature-repo-init:
	@echo "Initializing Feast feature repository..."
	rm -rf feature_repo
	uv run feast init

docs-serve:
	@echo "Starting documentation server at http://0.0.0.0:8000"
	uv run mkdocs serve --dev-addr 0.0.0.0:8000

docs-build:
	@echo "Building documentation site..."
	uv run mkdocs build

docs-preview:
	@echo "Serving built documentation site from site/ directory..."
	@cd site && python -m http.server 8000
