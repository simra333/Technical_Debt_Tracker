import unittest
import json
from app import create_app, db
from app.models import TechnicalDebt
from config import TestConfig


class TestApiAuth(unittest.TestCase):

    def setUp(self):
        """Set up a test fixture before each test."""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up test fixtures after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_requires_login(self):
        """Test GET is blocked without login"""
        response = self.client.get('/api/debts')

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')

    def test_post_requires_login(self):
        """Test POST is blocked without login"""
        debt_data = {
            "title": "Test Debt",
            "description": "This is a test item",
            "category": "Architectural Debt",
            "risk": 5,
            "effort_estimate": 3,
            "status": "Open",
            "assigned_to": "Alice"
        }

        response = self.client.post(
            '/api/debts',
            data=json.dumps(debt_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')

        # Ensure nothing was created
        with self.app.app_context():
            self.assertEqual(TechnicalDebt.query.count(), 0)

    def test_put_requires_login(self):
        """Test PUT is blocked without login"""

        # Create a record directly in DB
        with self.app.app_context():
            debt = TechnicalDebt(
                title="Original",
                description="Before update",
                category="Architectural Debt",
                risk=3,
                effort_estimate=2,
                status="Open",
                assigned_to="Alice"
            )
            db.session.add(debt)
            db.session.commit()
            debt_id = debt.id

        updated_data = {
            "title": "Updated",
            "description": "After update",
            "category": "Architectural Debt",
            "risk": 1,
            "effort_estimate": 1,
            "status": "Resolved",
            "assigned_to": "Bob"
        }

        response = self.client.put(
            f'/api/debts/{debt_id}',
            data=json.dumps(updated_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')

        # Ensure record was NOT updated
        with self.app.app_context():
            unchanged = db.session.get(TechnicalDebt, debt_id)
            self.assertEqual(unchanged.title, "Original")
            self.assertEqual(unchanged.status, "Open")

    def test_delete_requires_login(self):
        """Test DELETE is blocked without login"""

        # Create a record directly in DB
        with self.app.app_context():
            debt = TechnicalDebt(
                title="To delete",
                description="Should remain",
                category="Architectural Debt",
                risk=2,
                effort_estimate=1,
                status="Open",
                assigned_to="Alice"
            )
            db.session.add(debt)
            db.session.commit()
            debt_id = debt.id

        response = self.client.delete(f'/api/debts/{debt_id}')

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')

        # Ensure record still exists
        with self.app.app_context():
            still_exists = db.session.get(TechnicalDebt, debt_id)
            self.assertIsNotNone(still_exists)