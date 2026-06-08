import unittest
import os
import sqlite3
from app import app, init_db
from flask import session

DATABASE = 'taskflow.db'

class AuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        # Clean up old database and reinitialize
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
        init_db()
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        # Clean up after tests
        if os.path.exists(DATABASE):
            os.remove(DATABASE)

    def test_signup(self):
        response = self.app.post('/signup', data={
            'name': 'TestUser',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully! Please log in.', response.data)

    def test_login_success(self):
        self.app.post('/signup', data={
            'name': 'TestUser',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        response = self.app.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully!', response.data)
        with self.app.session_transaction() as sess:
            self.assertEqual(sess['user_name'], 'TestUser')

    def test_login_failure(self):
        response = self.app.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password.', response.data)

    def test_logout(self):
        self.app.post('/signup', data={
            'name': 'TestUser',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.app.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out.', response.data)
        with self.app.session_transaction() as sess:
            self.assertNotIn('user_name', sess)

if __name__ == '__main__':
    unittest.main()