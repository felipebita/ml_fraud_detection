# src/data/data_loader.py

from pathlib import Path

import pandas as pd

from src.data.data_processing import DataProcessor
from src.data.data_profiler import DataProfiler
from src.data.data_validator import DataValidator
from src.utils.config import get_config
from src.utils.logger import LoggerContext, get_logger, log_data_info

logger = get_logger(__name__)


def load_data() -> pd.DataFrame:
    """
    Loads transaction data from the path specified in the configuration.

    Returns:
        pd.DataFrame: A DataFrame containing the raw transaction data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file is empty.
    """
    config = get_config()
    file_path = Path(config["data"]["raw_path"])

    with LoggerContext(logger, "load_data", file_path=str(file_path)):
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found at: {file_path}")

        logger.info("File found. Attempting to load into pandas DataFrame.")

        try:
            df = pd.read_csv(file_path)
            if df.empty:
                raise ValueError("Data file is empty.")
        except pd.errors.EmptyDataError:
            raise ValueError("Data file is empty or malformed.")
        except Exception as e:
            logger.error("Failed to load CSV file.", error=str(e))
            raise

        log_data_info(logger, df, dataset_name="raw_data")
        return df


if __name__ == "__main__":
    logger.info("--- Starting Data Ingestion & Validation Pipeline ---")
    config = get_config()

    try:
        # 1. Load raw data
        raw_df = load_data()

        # 2. Profile the true raw data
        logger.info("--- Profiling Raw Data ---")
        raw_profile_path = config["data"]["raw_profile_path"]
        raw_profiler = DataProfiler(raw_df)
        raw_profiler.generate_profile()
        raw_profiler.export_profile(raw_profile_path)

        # 3. Perform DataFrame-level validation with Pandera
        validator = DataValidator()
        validated_df = validator.validate(raw_df)

        # 4. Process the validated data
        processor = DataProcessor()
        standardized_df = processor.standardize(validated_df)
        filtered_df = processor.filter_transaction_types(standardized_df)
        encoded_df = processor.encode_transaction_type(filtered_df)

        # 5. Profile the final, processed data
        logger.info("--- Profiling Processed Data ---")
        processed_profile_path = config["data"]["processed_profile_path"]
        processed_profiler = DataProfiler(encoded_df)
        processed_profiler.generate_profile()
        processed_profiler.export_profile(processed_profile_path)

        # 6. Save the final, trusted DataFrame
        output_path = Path(config["data"]["processed_path"])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with LoggerContext(
            logger, "save_processed_data", output_file=str(output_path)
        ) as log_context:
            encoded_df.to_parquet(output_path, index=False)
            log_data_info(logger, encoded_df, dataset_name="final_processed_data")
            logger.info("Processed data saved successfully.")

    except (FileNotFoundError, ValueError) as e:
        logger.error("Pipeline failed.", error=str(e), exc_info=True)
        exit(1)
    except Exception as e:
        logger.critical(
            "An unexpected error occurred during the pipeline execution.",
            error=str(e),
            exc_info=True,
        )
        exit(1)

    logger.info("--- Data Ingestion & Validation Pipeline Finished ---")
