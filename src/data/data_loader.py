# src/data/data_loader.py

import os
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, ValidationError

from src.data.data_validator import DataValidator
from src.utils.logger import LoggerContext, get_logger, log_data_info

logger = get_logger(__name__)


class TransactionSchema(BaseModel):
    """
    Pydantic schema for validating the structure and types of a single transaction row.
    This is based on the columns from the PaySim dataset.
    """

    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFraud: int
    isFlaggedFraud: int


def load_data(file_name: str = "raw.csv") -> pd.DataFrame:
    """
    Loads transaction data from a CSV file, validates it against a Pydantic
    schema, and returns a clean DataFrame.

    Args:
        file_name (str): The name of the CSV file to load from the raw data path.

    Returns:
        pd.DataFrame: A DataFrame containing the validated transaction data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file is empty or contains no valid data after validation.
    """
    with LoggerContext(logger, "load_data", file_name=file_name) as log_context:
        # 1. Resolve data path from environment variables
        raw_data_path_str = os.getenv("RAW_DATA_PATH", "./data/raw")
        file_path = Path(raw_data_path_str) / file_name
        log_context.context["file_path"] = str(file_path)

        # 2. Check for file existence
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found at: {file_path}")

        logger.info("File found. Attempting to load into pandas DataFrame.")

        # 3. Load data with basic error handling
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                raise ValueError("Data file is empty.")
        except pd.errors.EmptyDataError:
            raise ValueError("Data file is empty or malformed.")
        except Exception as e:
            logger.error("Failed to load CSV file.", error=str(e))
            raise

        # 4. Validate data row-by-row using Pydantic
        valid_records: list[dict] = []
        invalid_row_count = 0

        logger.info("Starting Pydantic validation for each row...", total_rows=len(df))
        for index, row in df.iterrows():
            try:
                # Convert row to dict and validate
                validated_record = TransactionSchema(**row.to_dict()).model_dump()
                valid_records.append(validated_record)
            except ValidationError as e:
                invalid_row_count += 1
                if invalid_row_count <= 5:
                    logger.warning(
                        "Row validation failed.",
                        row_index=index,
                        error_details=e.errors(),
                        row_data=row.to_dict(),
                    )

        log_context.context["total_rows_in_file"] = len(df)
        log_context.context["valid_rows_found"] = len(valid_records)
        log_context.context["invalid_rows_skipped"] = invalid_row_count

        if not valid_records:
            raise ValueError(
                "No valid transaction data found in the file after validation."
            )

        # 5. Create final DataFrame and log summary
        validated_df = pd.DataFrame(valid_records)
        log_data_info(logger, validated_df, dataset_name="pydantic_validated_data")

        return validated_df


if __name__ == "__main__":
    logger.info("--- Starting Data Ingestion & Validation Pipeline ---")

    try:
        # 1. Load data with initial Pydantic validation
        initial_df = load_data(file_name="raw.csv")

        # 2. Perform DataFrame-level validation with Pandera
        validator = DataValidator()
        validated_df = validator.validate(initial_df)

        # 3. Standardize the validated data
        standardized_df = validator.standardize(validated_df)

        # 4. Save the final, trusted DataFrame
        processed_data_path_str = os.getenv("PROCESSED_DATA_PATH", "./data/processed")
        output_path = Path(processed_data_path_str)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / "transactions.parquet"

        with LoggerContext(
            logger, "save_processed_data", output_file=str(output_file)
        ) as log_context:
            standardized_df.to_parquet(output_file, index=False)
            log_data_info(logger, standardized_df, dataset_name="final_processed_data")
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
