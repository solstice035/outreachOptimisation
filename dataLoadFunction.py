import os
import pandas as pd
import logging
import dask.dataframe as dd
import time


def process_engagement_data(
    file_path,
    start_row=0,
    keep_cols=None,
    date_cols=None,
    service_line="Consulting",
    verbose=True,
):
    """
    Processes an Excel file containing engagement data, filters and formats the data, and adds calculated columns.

    Args:
        file_path (str): The path to the Excel file.
        start_row (int, optional): The row to start reading data from. Defaults to 0.
        keep_cols (list, optional): List of columns to keep. Defaults to a predefined list.
        date_cols (list, optional): List of columns to convert to datetime. Defaults to a predefined list.
        service_line (str, optional): The service line to filter by. Defaults to 'Consulting'.
        verbose (bool, optional): If True, print and log additional information. Defaults to True.

    Returns:
        pd.DataFrame: The processed DataFrame.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If invalid arguments are provided.
        Exception: For other errors that occur during processing.
    """
    # Configure logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)

    if not isinstance(start_row, int) or start_row < 0:
        raise ValueError("start_row must be a non-negative integer.")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    if keep_cols is None:
        keep_cols = [
            "Engagement ID",
            "Creation Date",
            "Release Date",
            "Last Time Charged Date",
            "Last Expenses Charged Date",
            "Last Active ETC-P Date",
            "Engagement",
            "Client",
            "Engagement Partner",
            "Engagement Partner GUI",
            "Engagement Manager",
            "Engagement Manager GUI",
            "Engagement Partner Service Line",
            "Engagement Status",
        ]

    if date_cols is None:
        date_cols = [
            "Creation Date",
            "Release Date",
            "Last Time Charged Date",
            "Last Expenses Charged Date",
            "Last Active ETC-P Date",
        ]

    try:
        logger.info(f"File Path: {file_path}")

        # Load the Excel data into a DataFrame using Dask for parallel processing
        start_time = time.time()
        df_raw = dd.read_excel(file_path, skiprows=start_row).compute()
        logger.info(f"Data loaded with shape: {df_raw.shape}")
        logger.info(f"Data loading time: {time.time() - start_time:.2f} seconds")

        # Reduce columns to only the ones needed
        start_time = time.time()
        df_filtered = df_raw[keep_cols]
        logger.info(f"Data reduced with shape: {df_filtered.shape}")
        logger.info(f"Column reduction time: {time.time() - start_time:.2f} seconds")

        # Filter the data
        df_filtered = df_filtered[
            (
                df_filtered["Engagement Partner Service Line"].str.lower()
                == service_line.lower()
            )
            & (df_filtered["Engagement Status"] == "Released")
        ]
        logger.info(f"Data filtered with shape: {df_filtered.shape}")

        # Convert date columns to datetime in a single step
        start_time = time.time()
        df_filtered[date_cols] = df_filtered[date_cols].apply(pd.to_datetime)
        logger.info(f"Date conversion time: {time.time() - start_time:.2f} seconds")

        # Add temporary calculated columns
        start_time = time.time()
        df_filtered["Last ETC Date"] = df_filtered["Last Active ETC-P Date"].fillna(
            df_filtered["Release Date"]
        )
        df_filtered["Data Date"] = df_filtered["Last Time Charged Date"].max()

        # Calculate the age of ETC in days using date offset
        df_filtered["ETC Age"] = (
            df_filtered["Data Date"] - df_filtered["Last ETC Date"]
        ).dt.days

        # Reset index
        df_filtered.reset_index(drop=True, inplace=True)
        logger.info(
            f"Temporary column addition and index reset time: {time.time() - start_time:.2f} seconds"
        )

        # Log data types
        logger.info(f"Data Types: {df_filtered.dtypes}")

        return df_filtered

    except FileNotFoundError as fnf_error:
        logger.error(f"File not found: {fnf_error}")
        raise
    except ValueError as val_error:
        logger.error(f"Value error: {val_error}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


# Example usage:
# df_processed = process_engagement_data("./inputData/PreviousWeeksEngagementLists/20240510 Engagement List.xlsx")
