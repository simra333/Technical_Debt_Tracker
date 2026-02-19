import unittest
from app import create_app, db
from app.models import TechnicalDebt
from datetime import datetime

class TestTechnicalDebtModel(unittest.TestCase):
    def setUp(self): 
        """Set up a test fixtures before each test."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up test fixtures after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_technical_debt(self):
        """Test creating a new technical debt item."""
        debt = TechnicalDebt(
            title="Test Debt 1",
            description="This is a test item",
            risk="High",
            effort_estimate="Medium",
            status="Open",
            assigned_to="Alice",
            created_at=datetime.now()
        )
        db.session.add(debt)
        db.session.commit()

        saved = TechnicalDebt.query.first()

        self.assertIsNotNone(saved)
        self.assertEqual(saved.title, "Test Debt 1")
        self.assertEqual(saved.description, "This is a test item")
        self.assertEqual(saved.risk, "High")
        self.assertEqual(saved.effort_estimate, "Medium")
        self.assertEqual(saved.status, "Open")
        self.assertEqual(saved.assigned_to, "Alice")
        self.assertIsInstance(saved.created_at, datetime)

if __name__ == '__main__':
    unittest.main()
