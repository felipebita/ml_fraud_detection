
# Makefile for the Fraud Detection project

.PHONY: help setup data train evaluate test serve dashboard

help:
	@echo "Commands:"
	@echo "  setup          : Initial project setup"
	@echo "  lint           : Run linting checks (ruff)"
	@echo "  type-check     : Run type checking (mypy)"
	@echo "  format         : Format code (black)"
	@echo "  pre-commit     : Run pre-commit hooks"
	@echo "  test           : Run all tests"
	@echo "  data           : Run data pipeline"
	@echo "  train          : Train models"
	@echo "  evaluate       : Evaluate models"

	@echo "  serve          : Start model server"
	@echo "  dashboard      : Launch MLflow UI"

setup:
	@echo "Setting up the project..."
	uv sync --all-extras
	uv run pre-commit install

data:
	@echo "Running the data pipeline..."
	# Add data pipeline commands here

train:
	@echo "Training models..."
	# Add model training commands here

evaluate:
	@echo "Evaluating models..."
	# Add model evaluation commands here

lint:
	@echo "Linting code..."
	ruff check src/ tests/ --fix

type-check:
	@echo "Type-checking code..."
	mypy src/

format:
	@echo "Formating code..."
	black src/ tests/

pre-commit:
	@echo "Runnin pre-commit hooks..."
	uv run pre-commit run --all-files

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

serve:
	@echo "Starting the model server..."
	# Add model serving commands here

dashboard:
	@echo "Launching MLflow UI..."
	@./scripts/start_mlflow_duckdb.sh
