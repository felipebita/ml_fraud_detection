"""Fraud Detection ML Project"""

from src.utils.logger import get_logger, setup_logging

# Initialize logging on import
# The setup_logging function now reads configuration from files and environment variables
setup_logging()

# Create package-level logger
logger = get_logger(__name__)
logger.info("fraud_detection_package_initialized", version="0.1.0")
