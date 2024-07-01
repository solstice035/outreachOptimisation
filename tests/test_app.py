import os
import unittest
from datetime import datetime
from flask import Flask, session
from app import app, process_engagement_data, load_data_to_db
import pandas as pd


class FlaskAppTests(unittest.TestCase):
    """
    Flask application test cases to ensure the application routes and functionalities
    work as expected.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment before any tests run. This includes setting the
        Flask app to testing mode, creating test directories, and initializing the
        test client.
        """
        cls.app = app
        cls.client = cls.app.test_client()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.app.config["UPLOAD_FOLDER"] = "./tests_uploads"
        cls.app.config["LOG_FOLDER"] = "./test_logs"

        # Ensure the test directories exist
        os.makedirs(cls.app.config["LOAD_FOLDER"], exist_ok=True)
        os.makedirs(cls.app.config["LOG_FOLDER"], exist_ok=True)

        # Create a valid Excel test file for upload with the required columns
        test_file_path = os.path.join(cls.app.config["LOAD_FOLDER"], "test_file.xlsx")
        df = pd.DataFrame(
            {
                "Engagement ID": [1, 2, 3],
                "Creation Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Release Date": ["2023-02-01", "2023-02-02", "2023-02-03"],
                "Last Time Charged Date": ["2023-03-01", "2023-03-02", "2023-03-03"],
                "Last Expenses Charged Date": [
                    "2023-04-01",
                    "2023-04-02",
                    "2023-04-03",
                ],
                "Last Active ETC-P Date": ["2023-05-01", "2023-05-02", "2023-05-03"],
                "Engagement": ["Engagement 1", "Engagement 2", "Engagement 3"],
                "Client": ["Client 1", "Client 2", "Client 3"],
                "Engagement Partner": ["Partner 1", "Partner 2", "Partner 3"],
                "Engagement Partner GUI": ["GUI 1", "GUI 2", "GUI 3"],
                "Engagement Manager": ["Manager 1", "Manager 2", "Manager 3"],
                "Engagement Manager GUI": ["MGR GUI 1", "MGR GUI 2", "MGR GUI 3"],
                "Engagement Partner Service Line": [
                    "Service Line 1",
                    "Service Line 2",
                    "Service Line 3",
                ],
                "Engagement Status": ["Active", "Inactive", "Active"],
            }
        )
        df.to_excel(test_file_path, index=False)

        # Create a valid Excel test file for process with the required columns
        process_file_path = os.path.join(
            cls.app.config["LOAD_FOLDER"], "process_test_file.xlsx"
        )
        df_process = pd.DataFrame(
            {
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
        )
        df_process.to_excel(process_file_path, index=False)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the test environment after all tests have run. This includes removing
        the test directories.
        """
        import shutil

        shutil.rmtree(cls.app.config["UPLOAD_FOLDER"])
        shutil.rmtree(cls.app.config["LOG_FOLDER"])

    def test_home_page(self):
        """
        Test the home page route to ensure it is accessible and contains the expected
        content.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Home", response.data)

    def test_upload_page_get(self):
        """
        Test the upload page route using a GET request to ensure it is accessible and
        contains the expected content.
        """
        response = self.client.get("/load")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upload and Preview Excel File", response.data)

    def test_upload_page_post(self):
        """
        Test the upload page route using a POST request to simulate a file upload and
        ensure the file upload functionality works as expected.
        """
        data = {"start_row": 1, "service_line": "Service Line 1"}
        # Use the valid test file here
        test_file_path = os.path.join(
            self.app.config["LOAD_FOLDER"], "test_file.xlsx"
        )
        with open(test_file_path, "rb") as test_file:
            data["file"] = (test_file, "test_file.xlsx")
            response = self.client.post(
                "/upload",
                data=data,
                content_type="multipart/form-data",
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"File loaded successfully.", response.data)

    def test_process_data(self):
        """
        Test the data processing functionality by simulating a form submission with
        session data and ensuring the processing works as expected.
        """
        with self.client.session_transaction() as sess:
            sess["file_path"] = os.path.join(
                self.app.config["LOAD_FOLDER"], "process_test_file.xlsx"
            )
            sess["upload_timestamp"] = "20230101_000000"

        data = {"start_row": 1, "service_line": "Assurance", "export_log": False}
        response = self.client.post("/process", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Data processed successfully.", response.data)

        # TODO: #9 Fix the above unit test, expected columns not working correctly

    def test_404_error(self):
        """
        Test a non-existent route to ensure it returns a 404 status code and contains
        the expected content.
        """
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404 Not Found", response.data)


if __name__ == "__main__":
    unittest.main()

# to run: python -m unittest tests/test_app.py
