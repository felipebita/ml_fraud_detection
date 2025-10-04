import logging
import os
import sys
import zipfile

import gdown
import pandas as pd

from src.utils.config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def download_data(config):
    """Download the dataset from Google Drive."""
    file_id = config["data_setup"]["gdrive_file_id"]
    download_path = config["data_setup"]["download_path"]
    zip_file_path = os.path.join(download_path, "dataset.zip")

    logging.info(
        f"Downloading dataset from Google Drive (ID: {file_id}) to {zip_file_path}..."
    )
    os.makedirs(download_path, exist_ok=True)

    try:
        gdown.download(id=file_id, output=zip_file_path, quiet=False)
        logging.info("Dataset downloaded successfully.")
        return zip_file_path
    except Exception as e:
        logging.error(f"Failed to download dataset from Google Drive: {e}")
        sys.exit(1)


def unzip_data(zip_file_path, config):
    """Unzip the downloaded file."""
    download_path = config["data_setup"]["download_path"]
    logging.info(f"Unzipping {zip_file_path} to {download_path}...")
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(download_path)
        logging.info("Unzipped successfully.")
    except Exception as e:
        logging.error(f"Failed to unzip the dataset: {e}")
        sys.exit(1)


def find_csv_file(config):
    """Find the name of the downloaded CSV file."""
    download_path = config["data_setup"]["download_path"]
    try:
        files = os.listdir(download_path)
        csv_files = [f for f in files if f.endswith(".csv")]
        if not csv_files:
            logging.error(f"No CSV file found in {download_path}")
            sys.exit(1)
        return os.path.join(download_path, csv_files[0])
    except FileNotFoundError:
        logging.error(f"Download directory not found: {download_path}")
        sys.exit(1)


def process_data(csv_file, config):
    """Read the CSV, select the first configured number of rows, and save it."""
    num_rows = config["data_setup"]["num_rows_to_select"]
    output_file = config["data"]["raw_path"]
    raw_path_dir = os.path.dirname(output_file)

    logging.info(f"Processing {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
        logging.info(f"Read {len(df)} rows from the original dataset.")

        df_subset = df.head(num_rows)
        logging.info(f"Selected the first {len(df_subset)} rows.")

        os.makedirs(raw_path_dir, exist_ok=True)
        df_subset.to_csv(output_file, index=False)
        logging.info(f"Saved processed data to {output_file}")
    except Exception as e:
        logging.error(f"An error occurred during data processing: {e}")
        sys.exit(1)


def main():
    """Main function to orchestrate the data setup process."""
    config = get_config()
    zip_file_path = download_data(config)
    unzip_data(zip_file_path, config)
    csv_file = find_csv_file(config)
    process_data(csv_file, config)


if __name__ == "__main__":
    main()
