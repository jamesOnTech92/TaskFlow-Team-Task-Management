# TaskFlow Accounts and Authentication

This repository contains a focused Flask + SQLite implementation of TaskFlow's accounts and authentication feature.

## Features

- Sign up with name, email, and password
- Log in with email and password
- Log out
- Server-side sessions using `Flask-Session`
- SQLite `users` table with:
  - `name`
  - `email`
  - `password_hash`
- Minimum password length rule: **8 characters**

## Requirements

Install dependencies:

```bash
pip install flask flask-session
```

## Run

```bash
python app.py
```

The app will create a local SQLite database file named `taskflow.db` automatically on first run.

## Notes

- Passwords are stored securely as hashes using Werkzeug.
- Sessions are stored on the server filesystem in `.flask_session/`.
- The app is intentionally minimal and focused only on accounts/authentication.
