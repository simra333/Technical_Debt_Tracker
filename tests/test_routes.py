import unittest
import json
from app import create_app, db
from app.models import TechnicalDebt
from config import TestConfig

class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up a test fixture before each test."""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

        # Simulate a logged-in user (so @api_login_required passes)
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
        
    def tearDown(self):
        """Clean up test fixtures after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_technical_debt(self):
        """Test creating a new technical debt item via a POST request"""
        # 1. Prepare test data
        debt_data = {
            "title": "Test Debt 1",
            "description": "This is a test item",
            "category": "Architectural Debt",
            "risk": 5,
            "effort_estimate": 3,
            "status": "Open",
            "assigned_to": "Alice"
        }

        # 2. Make a POST request to create a new technical debt item
        response = self.client.post(
            '/api/debts',
            data=json.dumps(debt_data),
            content_type='application/json'
        )

        # 3. Check the response status code and content
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Test Debt 1')
        self.assertEqual(data['description'], 'This is a test item')
        self.assertEqual(data['category'], 'Architectural Debt')
        self.assertEqual(data['risk'], 5)
        self.assertEqual(data['effort_estimate'], 3)
        self.assertEqual(data['status'], 'Open')
        self.assertEqual(data['assigned_to'], 'Alice')


    def test_get_technical_debt(self):
        """Test retrieving all technical debt items via a GET request"""
        with self.app.app_context():
            # Create test data
            debt1 = TechnicalDebt(
                title="Test Debt 1",
                description="This is a test item",
                category="Architectural Debt",
                risk=5,
                effort_estimate=3,
                status="Open",
                assigned_to="Alice"
            )
            debt2 = TechnicalDebt(
                title="Test Debt 2",
                description="This is another test item",
                category="Architectural Debt",
                risk=3,
                effort_estimate=1,
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

    def test_update_debt_items(self):
        """Test updating an existing technical debt item via a PUT request"""
        with self.app.app_context():
            # Create test data
            debt = TechnicalDebt(
                title="Test Debt 1",
                description="This is a test item",
                category="Architectural Debt",
                risk=5,
                effort_estimate=3,
                status="Open",
                assigned_to="Alice"
            )
            db.session.add(debt)
            db.session.commit()
            debt_id = debt.id

            # Prepare updated data
            updated_data = {
                "title": "Updated Test Debt 1",
                "description": "This is an updated test item",
                "category": "Architectural Debt",
                "risk": 1,
                "effort_estimate": 1,
                "status": "Resolved",
                "assigned_to": "Bob"
            }
            
            # Make a PUT request to update the technical debt item
            response = self.client.put(
                f'/api/debts/{debt_id}',
                data=json.dumps(updated_data),
                content_type='application/json'
            )

            # Check the response status code and content
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['title'], 'Updated Test Debt 1')
            self.assertEqual(data['description'], 'This is an updated test item')
            self.assertEqual(data['category'], 'Architectural Debt')
            self.assertEqual(data['risk'], 1)
            self.assertEqual(data['effort_estimate'], 1)
            self.assertEqual(data['status'], 'Resolved')
            self.assertEqual(data['assigned_to'], 'Bob')

            # Verify the item was updated in the database
            with self.app.app_context():
                updated_debt = db.session.get(TechnicalDebt, debt_id)
                self.assertEqual(updated_debt.title, 'Updated Test Debt 1')
                self.assertEqual(updated_debt.description, 'This is an updated test item')
                self.assertEqual(updated_debt.category, 'Architectural Debt')      
                self.assertEqual(updated_debt.risk, 1)
                self.assertEqual(updated_debt.effort_estimate, 1)
                self.assertEqual(updated_debt.status, 'Resolved')
                self.assertEqual(updated_debt.assigned_to, 'Bob')

    def test_delete_debt(self):
        """Test deleting an existing technical debt item via a DELETE request"""
        with self.app.app_context():
            # Create test data
            debt = TechnicalDebt(
                title="Test Debt 1",
                description="This is a test item",
                category="Architectural Debt",
                risk=5,
                effort_estimate=3,
                status="Open",
                assigned_to="Alice"
            )
            db.session.add(debt)
            db.session.commit()
            debt_id = debt.id

            # Make a DELETE request to delete the technical debt item
            response = self.client.delete(f'/api/debts/{debt_id}')
            self.assertEqual(response.status_code, 204)

            # Verify the item was deleted from the database
            with self.app.app_context():
                deleted_debt = db.session.get(TechnicalDebt, debt_id)
                self.assertIsNone(deleted_debt)

    def test_create_debt_rejects_missing_title(self):
        """Test that creating a technical debt item without a title is rejected"""

        with self.app.app_context():

            response = self.client.post(
                '/api/debts',
                data=json.dumps({
                    "description": "This item is missing a title",
                    "category": "Architectural Debt",
                    "risk": 5,
                    "effort_estimate": 3,
                    "status": "Open",
                    "assigned_to": "Alice"
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn("Title is required", data['message'])

            with self.app.app_context():
                self.assertEqual(TechnicalDebt.query.count(), 0)

    def test_create_debt_rejects_invalid_status(self):
        """Test that creating a technical debt item with an invalid status is rejected"""

        with self.app.app_context():

            response = self.client.post(
                '/api/debts',
                data=json.dumps({
                    "title": "Invalid Status Debt",
                    "description": "This item has an invalid status",
                    "category": "Architectural Debt",
                    "risk": 5,
                    "effort_estimate": 3,
                    "status": "Invalid_Status",
                    "assigned_to": "Alice"
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn("Invalid status", data['message'])

            with self.app.app_context():
                self.assertEqual(TechnicalDebt.query.count(), 0)

    def test_create_debt_rejects_invalid_category(self):
        """Test that creating a technical debt item with an invalid category is rejected"""

        with self.app.app_context():

            response = self.client.post(
                '/api/debts',
                data=json.dumps({
                    "title": "Invalid Category Debt",
                    "description": "This item has an invalid category",
                    "category": "Invalid_Category",
                    "risk": 5,
                    "effort_estimate": 3,
                    "status": "Open",
                    "assigned_to": "Alice"
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn("Invalid category", data['message'])

            with self.app.app_context():
                self.assertEqual(TechnicalDebt.query.count(), 0)

    def test_create_debt_rejects_non_integer_risk(self):
        """Test that creating a technical debt item with a non-integer risk is rejected"""

        with self.app.app_context():

            response = self.client.post(
                '/api/debts',
                data=json.dumps({
                    "title": "Non-integer Risk Debt",
                    "description": "This item has a non-integer risk",
                    "category": "Architectural Debt",
                    "risk": "High",
                    "effort_estimate": 3,
                    "status": "Open",
                    "assigned_to": "Alice"
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn("Invalid input", data['message'])

            with self.app.app_context():
                self.assertEqual(TechnicalDebt.query.count(), 0)

    def test_create_debt_rejects_non_integer_effort_estimate(self):
        """Test that creating a technical debt item with a non-integer effort estimate is rejected"""

        with self.app.app_context():

            response = self.client.post(
                '/api/debts',
                data=json.dumps({
                    "title": "Non-integer Effort Estimate Debt",
                    "description": "This item has a non-integer effort estimate",
                    "category": "Architectural Debt",
                    "risk": 5,
                    "effort_estimate": "High",
                    "status": "Open",
                    "assigned_to": "Alice"
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn("Invalid input", data['message'])

            with self.app.app_context():
                self.assertEqual(TechnicalDebt.query.count(), 0)
    

            