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

    def test_create_technical_debt(self):
        """Test creating a new technical debt item via a POST request"""
        # 1. Prepare test data
        debt_data = {
            "title": "Test Debt 1",
            "description": "This is a test item",
            "risk": "High",
            "effort_estimate": "Medium",
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
        self.assertEqual(data['risk'], 'High')
        self.assertEqual(data['effort_estimate'], 'Medium')
        self.assertEqual(data['status'], 'Open')
        self.assertEqual(data['assigned_to'], 'Alice')


    def test_get_technical_debt(self):
        """Test retrieving all technical debt items via a GET request"""
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

    def test_update_debt_items(self):
        """Test updating an existing technical debt item via a PUT request"""
        with self.app.app_context():
            # Create test data
            debt = TechnicalDebt(
                title="Test Debt 1",
                description="This is a test item",
                risk="High",
                effort_estimate="Medium",
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
                "risk": "Low",
                "effort_estimate": "Low",
                "status": "Closed",
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
            self.assertEqual(data['risk'], 'Low')
            self.assertEqual(data['effort_estimate'], 'Low')
            self.assertEqual(data['status'], 'Closed')
            self.assertEqual(data['assigned_to'], 'Bob')

            # Verify the item was updated in the database
            with self.app.app_context():
                updated_debt = db.session.get(TechnicalDebt, debt_id)
                self.assertEqual(updated_debt.title, 'Updated Test Debt 1')
                self.assertEqual(updated_debt.description, 'This is an updated test item')      
                self.assertEqual(updated_debt.risk, 'Low')
                self.assertEqual(updated_debt.effort_estimate, 'Low')
                self.assertEqual(updated_debt.status, 'Closed')
                self.assertEqual(updated_debt.assigned_to, 'Bob')
