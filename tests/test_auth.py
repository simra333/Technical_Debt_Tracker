import unittest
import json
from app import create_app, db
from app.models import TechnicalDebt, User
from app.auth.services import hash_password, verify_password
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
            db.engine.dispose()  

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(
            '/register',
            json={
                'username': 'testuser',
                'password': 'testpassword'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User registered successfully')

        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, 'testpassword')  # Ensure password is hashed

    def test_register_duplicate_username(self):
        """Test registration with duplicate username fails"""
        # First, register a user
        with self.app.app_context():
            user = User(
                username='testuser',
                password_hash=hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()

        # Attempt to register with the same username
        response = self.client.post(
            '/register',
            json={
                'username': 'testuser',
                'password': 'anotherpassword'
            }
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Username already exists')

    def test_login_missing_username(self):
        """Test login fails when username is missing"""
        response = self.client.post('/login', json={'password': 'testpassword'  })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid input')

    def test_login_missing_password(self):
        """Test login fails when password is missing"""
        response = self.client.post('/login', json={'username': 'testuser'})

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid input')

    def test_hash_password_success(self):
        """Test password hashing works correctly"""

        hashed = hash_password('plain_password')

        self.assertNotEqual('plain_password', hashed)  # Ensure it's actually hashed
        self.assertTrue(verify_password('plain_password', hashed))  # Verify it matches

    def test_hash_password_invalid_input(self):
        """Test hashing with invalid input raises error"""
        with self.assertRaises(ValueError):
            hash_password('')  # Empty string should raise error

        with self.assertRaises(ValueError):
            hash_password(None)  # None should raise error

        with self.assertRaises(ValueError):
            hash_password(123)  # Non-string should raise error

    def test_verify_password_invalid_input(self):
        """Test password verification with invalid input returns False"""
        self.assertFalse(verify_password('', 'hash'))  # Empty password
        self.assertFalse(verify_password(None, 'hash'))  # None password
        self.assertFalse(verify_password('plain_password', ''))  # Empty hash
        self.assertFalse(verify_password('plain_password', None))  # None hash

    def test_login_successful(self):
        """Test successful login with correct credentials"""
        # First, register a user
        with self.app.app_context():
            user = User(
                username='testuser',
                password_hash=hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()

        # Now attempt to log in
        response = self.client.post(
            '/login',
            json={
                'username': 'testuser',
                'password': 'testpassword'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Login successful')
            

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

    def test_get_by_id_requires_login(self):
        """Test GET by ID is blocked without login"""

        # Create a record directly in DB
        with self.app.app_context():
            debt = TechnicalDebt(
                title="To retrieve",
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

        response = self.client.get(f'/api/debts/{debt_id}')

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')

    def test_health_does_not_require_login(self):
        """Test /health endpoint is accessible without login"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_ui_index_requires_login(self):
        """Test UI index page is blocked without login"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.headers['Location'])

    def test_ui_add_requires_login(self):
        """Test UI add page is blocked without login"""
        response = self.client.get('/add')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.headers['Location'])