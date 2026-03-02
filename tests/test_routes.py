import unittest
import json
from app import create_app, db
from app.models import TechnicalDebt

class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up a test fixture before each test."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
        
    def tearDown(self):
        """Clean up test fixtures after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_technical_debt(self):
        """Test retrieving all technical debt items."""
        with self.app.app_context():
            # Create test data
            debt1 = TechnicalDebt(
                title="Test Debt 1",
                description="This is a test item",
                risk="High",
                effort_estimate="Medium",
                status="Open",
                assigned_to="Alice"
            )
            debt2 = TechnicalDebt(
                title="Test Debt 2",
                description="This is another test item",
                risk="Medium",
                effort_estimate="Low",
                status="Open",
                assigned_to="Bob"
            )
            db.session.add(debt1)
            db.session.add(debt2)
            db.session.commit()

            # Test GET endpoint
            response = self.client.get('/api/debts')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['title'], "Test Debt 1")
            self.assertEqual(data[1]['title'], "Test Debt 2")