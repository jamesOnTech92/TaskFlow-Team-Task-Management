# TaskFlow-Team-Task-Management

## Features Implemented

### Accounts and Authentication
- Users can sign up with their name, email, and password.
- Passwords must be at least 8 characters long.
- Passwords are securely hashed before saving in the SQLite database.
- Users can log in using their email and password.
- Server-side sessions are used for managing logged-in state.
- Users can log out to end their session.

SQLite is used as the database for storing user information with fields:
- `name` (String)
- `email` (String, unique)
- `password_hash` (String, hashed password)

Run the app using `python app.py`. Ensure dependencies like Flask, Flask-SQLAlchemy, and Werkzeug are installed.