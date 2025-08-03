
# Makefile for the Fraud Detection project

.PHONY: help setup data train evaluate test serve dashboard

help:
	@echo "Commands:"
	@echo "  setup          : Initial project setup"
	@echo "  data           : Run data pipeline"
	@echo "  train          : Train models"
	@echo "  evaluate       : Evaluate models"
	@echo "  test           : Run all tests"
	@echo "  serve          : Start model server"
	@echo "  dashboard      : Launch MLflow UI"

setup:
	@echo "Setting up the project..."
	# Add setup commands here, e.g., pip install -e .

data:
	@echo "Running the data pipeline..."
	# Add data pipeline commands here

train:
	@echo "Training models..."
	# Add model training commands here

evaluate:
	@echo "Evaluating models..."
	# Add model evaluation commands here

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

serve:
	@echo "Starting the model server..."
	# Add model serving commands here

dashboard:
	@echo "Launching MLflow UI..."
	@./scripts/start_mlflow_duckdb.sh
