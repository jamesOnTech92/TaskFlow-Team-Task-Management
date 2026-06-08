# TaskFlow-Team-Task-Management

## Accounts and Authentication Feature

This implementation includes basic functionality for signing up, logging in, logging out, and server-side session management for users of TaskFlow.

### Features
1. **Sign Up**: Endpoint `/signup` for registering users with fields `name`, `email`, and `password`. Enforces a minimum password length of 8 characters.
2. **Log In**: Endpoint `/login` for logging in users with `email` and `password`. Validates credentials and starts a session.
3. **Log Out**: Endpoint `/logout` for terminating the session.

### Prerequisites
1. Python 3.11 or later.
2. Install required dependencies:
   ```bash
   pip install flask werkzeug
   ```

### How to Run
1. Initialize the SQLite database:
   ```bash
   python -c 'from app import init_db; init_db()'
   ```
2. Verify endpoints by writing your own client or testing scripts.

### Tests
Unit tests for the authentication endpoints can be executed using:
```bash
PYTHONPATH=/home/user/work python -m unittest discover -s /home/user/work -p 'test_app.py'
```

### Users Table
The `users` table is created in SQLite with the following schema:
- `id`: Primary Key
- `name`: Text
- `email`: Text (unique)
- `password_hash`: Text

### Note
This repository and feature implementation simulate a focused authentication component for the TaskFlow project.
