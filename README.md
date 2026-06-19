# TaskFlow Accounts and Authentication

This repository contains a focused Flask + SQLite implementation of TaskFlow's accounts and authentication feature.

## Features

- User sign up
- User log in
- User log out
- Server-side sessions when `Flask-Session` is available, with secure Flask session fallback
- SQLite `users` table with:
  - `name`
  - `email`
  - `password_hash`
- Minimum password length rule: 8 characters

## Requirements

- Python 3
- Flask
- Optional: `Flask-Session` for filesystem-backed server-side sessions

Install dependencies if needed:

```bash
pip install flask flask-session
```

## Run

```bash
python app.py
```

The app will create `taskflow.db` automatically on first run.

## Routes

- `/` - Home page
- `/signup` - Create an account
- `/login` - Log in
- `/logout` - Log out

## Notes

- Passwords are stored as hashes using Werkzeug security helpers.
- Emails must be unique.
- The app uses SQLite and is intended to be a small, focused starting point for TaskFlow authentication.
