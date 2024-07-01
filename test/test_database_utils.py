import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
from datetime import datetime
from utilities.database_utils import create_table_if_not_exists, insert_data, load_data_to_db


class TestDatabaseFunctions(unittest.TestCase):

    @patch("database_utils.psycopg2.connect")
    def test_create_table_if_not_exists(self, mock_connect):
        """
        Test creating table if not exists.
        """
        mock_connection = mock_connect.return_value
        mock_cursor = mock_connection.cursor.return_value

        create_table_if_not_exists(mock_connection, "test_table")

        mock_cursor.execute.assert_called_once()
        self.assertTrue(
            "CREATE TABLE IF NOT EXISTS test_table"
            in mock_cursor.execute.call_args[0][0]
        )

    @patch("database_utils.psycopg2.connect")
    def test_insert_data(self, mock_connect):
        """
        Test inserting data into the database.
        """
        mock_connection = mock_connect.return_value
        mock_cursor = mock_connection.cursor.return_value

        # Create a sample DataFrame
        data = {
            "engagement_id": ["1", "2"],
            "creation_date": [datetime(2024, 5, 10), datetime(2024, 5, 11)],
            "release_date": [datetime(2024, 6, 10), datetime(2024, 6, 11)],
            "last_time_charged_date": [datetime(2024, 6, 1), datetime(2024, 6, 2)],
            "last_expenses_charged_date": [
                datetime(2024, 5, 30),
                datetime(2024, 5, 31),
            ],
            "last_active_etcp_date": [datetime(2024, 5, 15), None],
            "engagement": ["Eng1", "Eng2"],
            "client": ["Client1", "Client2"],
            "engagement_partner": ["Partner1", "Partner2"],
            "engagement_partner_gui": ["101", "102"],
            "engagement_manager": ["Manager1", "Manager2"],
            "engagement_manager_gui": ["201", "202"],
            "engagement_partner_service_line": ["Consulting", "Advisory"],
            "engagement_status": ["Released", "Released"],
            "last_etc_date": [datetime(2024, 5, 15), datetime(2024, 6, 11)],
            "report_date": [datetime(2024, 6, 1), datetime(2024, 6, 2)],
            "etc_age": [10, 10],
        }
        df = pd.DataFrame(data)

        insert_data(
            mock_connection, df, "test_table", datetime(2024, 6, 10), "test_user"
        )

        self.assertEqual(mock_cursor.execute.call_count, len(df))

    @patch("database_utils.psycopg2.connect")
    @patch("database_utils.create_table_if_not_exists")
    @patch("database_utils.insert_data")
    @patch("database_utils.flash")
    def test_load_data_to_db(
        self, mock_flash, mock_insert_data, mock_create_table, mock_connect
    ):
        """
        Test loading data to the database.
        """
        mock_connection = mock_connect.return_value
        mock_insert_data.return_value = None
        mock_create_table.return_value = None

        # Create a sample DataFrame
        data = {
            "engagement_id": ["1", "2"],
            "creation_date": [datetime(2024, 5, 10), datetime(2024, 5, 11)],
            "release_date": [datetime(2024, 6, 10), datetime(2024, 6, 11)],
            "last_time_charged_date": [datetime(2024, 6, 1), datetime(2024, 6, 2)],
            "last_expenses_charged_date": [
                datetime(2024, 5, 30),
                datetime(2024, 5, 31),
            ],
            "last_active_etcp_date": [datetime(2024, 5, 15), None],
            "engagement": ["Eng1", "Eng2"],
            "client": ["Client1", "Client2"],
            "engagement_partner": ["Partner1", "Partner2"],
            "engagement_partner_gui": ["101", "102"],
            "engagement_manager": ["Manager1", "Manager2"],
            "engagement_manager_gui": ["201", "202"],
            "engagement_partner_service_line": ["Consulting", "Advisory"],
            "engagement_status": ["Released", "Released"],
            "last_etc_date": [datetime(2024, 5, 15), datetime(2024, 6, 11)],
            "report_date": [datetime(2024, 6, 1), datetime(2024, 6, 2)],
            "etc_age": [10, 10],
        }
        df = pd.DataFrame(data)

        load_data_to_db(df, "test_table", datetime(2024, 6, 10), "test_user")

        mock_create_table.assert_called_once_with(mock_connection, "test_table")
        mock_insert_data.assert_called_once_with(
            mock_connection, df, "test_table", datetime(2024, 6, 10), "test_user"
        )
        mock_connection.close.assert_called_once()
        mock_flash.assert_called_once_with(
            "Data loaded into the database successfully.", "success"
        )


if __name__ == "__main__":
    unittest.main()
