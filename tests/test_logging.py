import unittest
import json
from unittest.mock import patch
from app import create_app
from config import TestConfig

class TestLoggingSetup(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

    @patch("app.routes.logger")
    def test_invalid_status_logs_metric(self, mock_logger):
        response = self.client.post(
            '/api/debts',
            data=json.dumps({
                "title": "Test",
                "description": "Test",
                "category": "Architectural Debt",
                "risk": 5,
                "effort_estimate": 3,
                "status": "INVALID",
                "assigned_to": "Alice"
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        mock_logger.warning.assert_called_with(
            "metric=debt_creation_failed count=1 reason=invalid_status"
        )

    @patch("app.routes.logger")
    def test_invalid_category_logs_metric(self, mock_logger):
        response = self.client.post(
            '/api/debts',
            data=json.dumps({
                "title": "Test",
                "description": "Test",
                "category": "INVALID",
                "risk": 5,
                "effort_estimate": 3,
                "status": "Open",
                "assigned_to": "Alice"
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        mock_logger.warning.assert_called_with(
            "metric=debt_creation_failed count=1 reason=invalid_category"
        )

    