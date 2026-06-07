# TaskFlow - Accounts and Authentication

## Features
- Sign up: Register a new user with a name, email, and password.
- Log in: Authenticate an existing user.
- Log out: End the authenticated session.
- Password rules: Enforce a minimum password length of 8 characters.
- Server-side sessions: Maintain session data for authenticated users.
- SQLite database for storage: User data stored in the `taskflow.db` file.

## Setup
1. Install dependencies:
   ```bash
   pip install flask flask_sqlalchemy werkzeug
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Test API endpoints:
   - Sign up: `POST /signup` with JSON payload `{"name": "John Doe", "email": "john@example.com", "password": "password123"}`.
   - Log in: `POST /login` with JSON payload `{"email": "john@example.com", "password": "password123"}`.
   - Log out: `POST /logout`.

   You can use tools like Postman or `curl` to interact with the API.

## Notes
- Ensure SQLite database file (`taskflow.db`) has appropriate write permissions for the application.