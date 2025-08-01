"""Fraud Detection ML Project"""

import os

from src.utils.logger import get_logger, setup_logging

# Initialize logging on import
environment = os.getenv("ENVIRONMENT", "development")
log_level = os.getenv("LOG_LEVEL", "INFO")
json_logs = os.getenv("LOG_FORMAT", "text").lower() == "json"

setup_logging(log_level=log_level, json_logs=json_logs, environment=environment)

# Create package-level logger
logger = get_logger(__name__)
logger.info("fraud_detection_package_initialized", version="0.1.0")
