import unittest
from unittest.mock import patch
import pandas as pd
from dataLoadFunction import (
    process_engagement_data,
)  # Replace 'dataLoadFunction' with the actual module name


class TestProcessEngagementData(unittest.TestCase):

    @patch("dataLoadFunction.os.path.exists")
    @patch("dataLoadFunction.pd.read_excel")
    def test_successful_processing(self, mock_read_excel, mock_path_exists):
        """
        Test successful processing with default service line filter.

        Mocks the data to be returned by pd.read_excel and checks the resulting
        DataFrame is correctly processed and filtered.
        """
        # Mock the file existence check
        mock_path_exists.return_value = True

        # Mock the data to be returned by pd.read_excel
        mock_data = {
            "Engagement ID": [1, 2],
            "Creation Date": ["2024-05-10", "2024-05-11"],
            "Release Date": ["2024-06-10", "2024-06-11"],
            "Last Time Charged Date": ["2024-06-01", "2024-06-02"],
            "Last Expenses Charged Date": ["2024-05-30", "2024-05-31"],
            "Last Active ETC-P Date": ["2024-05-15", None],
            "Engagement": ["Eng1", "Eng2"],
            "Client": ["Client1", "Client2"],
            "Engagement Partner": ["Partner1", "Partner2"],
            "Engagement Partner GUI": [101, 102],
            "Engagement Manager": ["Manager1", "Manager2"],
            "Engagement Manager GUI": [201, 202],
            "Engagement Partner Service Line": ["Consulting", "Advisory"],
            "Engagement Status": ["Released", "Released"],
        }
        mock_df = pd.DataFrame(mock_data)
        mock_read_excel.return_value = mock_df

        # Call the function
        df_processed = process_engagement_data("dummy_path.xlsx")

        # Check the processed DataFrame
        self.assertEqual(
            df_processed.shape, (1, 16)
        )  # Only 1 row should match the default filter criteria
        self.assertIn("ETC Age", df_processed.columns)
        self.assertIn("Data Date", df_processed.columns)
        self.assertEqual(
            df_processed["ETC Age"].iloc[0],
            (
                df_processed["Data Date"].iloc[0] - df_processed["Last ETC Date"].iloc[0]
            ).days,
        )

    @patch("dataLoadFunction.os.path.exists")
    @patch("dataLoadFunction.pd.read_excel")
    def test_custom_service_line_filter(self, mock_read_excel, mock_path_exists):
        """
        Test processing with a custom service line filter.

        Mocks the data to be returned by pd.read_excel and checks the resulting
        DataFrame is correctly filtered based on the custom service line.
        """
        # Mock the file existence check
        mock_path_exists.return_value = True

        # Mock the data to be returned by pd.read_excel
        mock_data = {
            "Engagement ID": [1, 2],
            "Creation Date": ["2024-05-10", "2024-05-11"],
            "Release Date": ["2024-06-10", "2024-06-11"],
            "Last Time Charged Date": ["2024-06-01", "2024-06-02"],
            "Last Expenses Charged Date": ["2024-05-30", "2024-05-31"],
            "Last Active ETC-P Date": ["2024-05-15", None],
            "Engagement": ["Eng1", "Eng2"],
            "Client": ["Client1", "Client2"],
            "Engagement Partner": ["Partner1", "Partner2"],
            "Engagement Partner GUI": [101, 102],
            "Engagement Manager": ["Manager1", "Manager2"],
            "Engagement Manager GUI": [201, 202],
            "Engagement Partner Service Line": ["Consulting", "Advisory"],
            "Engagement Status": ["Released", "Released"],
        }
        mock_df = pd.DataFrame(mock_data)
        mock_read_excel.return_value = mock_df

        # Call the function with custom service line
        df_processed = process_engagement_data(
            "dummy_path.xlsx", service_line="Advisory"
        )

        # Check the processed DataFrame
        self.assertEqual(
            df_processed.shape, (1, 16)
        )  # Only 1 row should match the custom filter criteria
        self.assertEqual(
            df_processed["Engagement Partner Service Line"].iloc[0], "Advisory"
        )

    @patch("dataLoadFunction.os.path.exists")
    @patch("dataLoadFunction.pd.read_excel")
    def test_invalid_start_row(self, mock_read_excel, mock_path_exists):
        """
        Test the function with an invalid start_row argument.

        Ensures the function raises a ValueError when start_row is negative.
        """
        mock_path_exists.return_value = True

        with self.assertRaises(ValueError):
            process_engagement_data("dummy_path.xlsx", start_row=-1)

    @patch("dataLoadFunction.os.path.exists")
    @patch("dataLoadFunction.pd.read_excel")
    def test_file_not_exists(self, mock_read_excel, mock_path_exists):
        """
        Test the function with a non-existent file.

        Ensures the function raises a FileNotFoundError when the file does not exist.
        """
        mock_path_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            process_engagement_data("dummy_path.xlsx")

    @patch("dataLoadFunction.os.path.exists")
    @patch("dataLoadFunction.pd.read_excel")
    def test_empty_dataframe(self, mock_read_excel, mock_path_exists):
        """
        Test the function with an empty DataFrame.

        Ensures the function handles an empty DataFrame correctly without errors.
        """
        mock_path_exists.return_value = True

        # Mock an empty DataFrame
        mock_df = pd.DataFrame(
            {
                "Engagement ID": [],
                "Creation Date": [],
                "Release Date": [],
                "Last Time Charged Date": [],
                "Last Expenses Charged Date": [],
                "Last Active ETC-P Date": [],
                "Engagement": [],
                "Client": [],
                "Engagement Partner": [],
                "Engagement Partner GUI": [],
                "Engagement Manager": [],
                "Engagement Manager GUI": [],
                "Engagement Partner Service Line": [],
                "Engagement Status": [],
            }
        )
        mock_read_excel.return_value = mock_df

        # Call the function
        df_processed = process_engagement_data("dummy_path.xlsx")

        # Check the processed DataFrame
        self.assertTrue(df_processed.empty)

    @patch("dataLoadFunction.os.path.exists")
    @patch("dataLoadFunction.pd.read_excel")
    def test_no_matching_service_line(self, mock_read_excel, mock_path_exists):
        """
        Test the function with no rows matching the default service line filter.

        Ensures the resulting DataFrame is empty when no rows match the filter criteria.
        """
        mock_path_exists.return_value = True

        # Mock the data to be returned by pd.read_excel
        mock_data = {
            "Engagement ID": [1, 2],
            "Creation Date": ["2024-05-10", "2024-05-11"],
            "Release Date": ["2024-06-10", "2024-06-11"],
            "Last Time Charged Date": ["2024-06-01", "2024-06-02"],
            "Last Expenses Charged Date": ["2024-05-30", "2024-05-31"],
            "Last Active ETC-P Date": ["2024-05-15", None],
            "Engagement": ["Eng1", "Eng2"],
            "Client": ["Client1", "Client2"],
            "Engagement Partner": ["Partner1", "Partner2"],
            "Engagement Partner GUI": [101, 102],
            "Engagement Manager": ["Manager1", "Manager2"],
            "Engagement Manager GUI": [201, 202],
            "Engagement Partner Service Line": ["Tax", "Advisory"],
            "Engagement Status": ["Released", "Released"],
        }
        mock_df = pd.DataFrame(mock_data)
        mock_read_excel.return_value = mock_df

        # Call the function
        df_processed = process_engagement_data("dummy_path.xlsx")

        # Check the processed DataFrame
        self.assertTrue(
            df_processed.empty
        )  # No rows should match the default filter criteria


if __name__ == "__main__":
    unittest.main()
