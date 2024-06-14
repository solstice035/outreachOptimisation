import unittest
from flask import Flask
from app import app

# FILEPATH: /Users/nicksolly/Dev/outreachOptimisation/tests/test_app.py


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_route(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to the Home Page", response.data)

    def test_upload_route(self):
        response = self.app.get("/upload")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upload Page", response.data)

    def test_add_delegate_route(self):
        response = self.app.get("/add_delegate")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add Delegate Page", response.data)

    def test_page_not_found(self):
        response = self.app.get("/nonexistent_route")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page Not Found", response.data)


if __name__ == "__main__":
    unittest.main()
