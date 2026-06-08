import unittest
from app import app, db, User
from werkzeug.security import generate_password_hash

class TaskFlowAuthTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_users.db'
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_sign_up(self):
        response = self.app.post('/sign-up', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirects after signup
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertTrue(user.name == 'Test User')

    def test_login(self):
        with app.app_context():
            hashed_password = generate_password_hash('password123', method='pbkdf2:sha256')
            user = User(name='Test User', email='test@example.com', password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()

        response = self.app.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirects after login
        with self.app as client:
            client.get('/logout')
            self.assertIn(b'Welcome', client.get('/').data)

    def test_logout(self):
        with self.app as client:
            with client.session_transaction() as session:
                session['user_id'] = 1
                session['user_name'] = 'Test User'

            response = client.get('/logout')
            self.assertEqual(response.status_code, 302)  # Redirects after logout
            self.assertNotIn('user_id', session)

if __name__ == '__main__':
    unittest.main()