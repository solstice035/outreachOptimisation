import os
import pandas as pd
import logging
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

        # Load the Excel data into a DataFrame
        start_time = time.time()
        df_raw = pd.read_excel(file_path, skiprows=start_row)
        logger.info(f"Data loaded with shape (rows and columns): {df_raw.shape}")
        logger.info(f"Data loading time: {time.time() - start_time:.2f} seconds")

        # Reduce columns to only the ones needed
        start_time = time.time()
        df_filtered = df_raw[keep_cols]
        logger.info(f"Data reduced to key columns only: {df_filtered.shape}")
        logger.info(f"Column reduction time: {time.time() - start_time:.2f} seconds")

        # Ensure the column to be filtered is of string type
        df_filtered.loc[:, "Engagement Partner Service Line"] = df_filtered.loc[
            :, "Engagement Partner Service Line"
        ].astype(str)

        # Filter the data
        df_filtered = df_filtered[
            (
                df_filtered.loc[:, "Engagement Partner Service Line"].str.lower()
                == service_line.lower()
            )
            & (df_filtered["Engagement Status"] == "Released")
        ]
        logger.info(
            f"Data filtered by EP service line and released eng. codes only. Filtered data shape: {df_filtered.shape}"
        )

        # Convert date columns to datetime in a single step
        start_time = time.time()
        for col in date_cols:
            df_filtered[col] = pd.to_datetime(df_filtered[col], errors="coerce")

        # Add calculated columns
        df_filtered["Last ETC Date"] = df_filtered["Last Active ETC-P Date"].fillna(
            df_filtered["Release Date"]
        )
        df_filtered["Report Date"] = df_filtered["Last Time Charged Date"].max()

        # Calculate the age of ETC in days using date offset
        df_filtered["ETC Age"] = (
            df_filtered["Report Date"] - df_filtered["Last ETC Date"]
        ).dt.days

        # Convert NAT values to none in date columns
        df_filtered[date_cols] = (
            df_filtered[date_cols]
            .astype(object)
            .where(pd.notnull(df_filtered[date_cols]), None)
        )

        # TODO: Fix issue above to allow upload of NAT values to SQL. Currently coverting dtype to object to allow upload @line 119

        # Replace space with underscore and all punctuation from column headers and convert to lowercase
        df_filtered.columns = (
            df_filtered.columns.str.replace(" ", "_").str.replace("-", "").str.lower()
        )

        # Reset index
        df_filtered.reset_index(drop=True, inplace=True)
        logger.info(
            f"Added calculated columns, new data shape: {df_filtered.shape} and time taken: {time.time() - start_time:.2f} seconds"
        )

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
