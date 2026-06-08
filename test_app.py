import unittest
import json
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_signup(self):
        response = self.client.post('/signup', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully.', response.get_data(as_text=True))

    def test_signup_missing_fields(self):
        response = self.client.post('/signup', json={
            'name': 'Test User',
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('All fields are required.', response.get_data(as_text=True))

    def test_login(self):
        # Ensure user exists before login
        self.client.post('/signup', json={
            'name': 'Test User',
            'email': 'test_login@example.com',
            'password': 'password123'
        })
        
        response = self.client.post('/login', json={
            'email': 'test_login@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logged in successfully.', response.get_data(as_text=True))

    def test_login_invalid_credentials(self):
        response = self.client.post('/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid credentials.', response.get_data(as_text=True))

    def test_logout(self):
        # Ensure user logs in before logout
        self.client.post('/signup', json={
            'name': 'Test User',
            'email': 'test_logout@example.com',
            'password': 'password123'
        })
        self.client.post('/login', json={
            'email': 'test_logout@example.com',
            'password': 'password123'
        })
        
        response = self.client.post('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logged out successfully.', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()