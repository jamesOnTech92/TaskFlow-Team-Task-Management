# TaskFlow Accounts and Authentication

Focused Flask + SQLite implementation of TaskFlow's accounts and authentication feature.

## Included

- User sign up
- User log in
- User log out
- Server-side sessions with Flask
- SQLite `users` table
- Password hashing
- Minimum password length of 8 characters

## Users Table

The app creates a `users` table automatically with these fields:

- `id`
- `name`
- `email`
- `password_hash`

## Requirements

- Python 3
- Flask

Install Flask if needed:

```bash
pip install flask
```

## Run

```bash
python app.py
```

This creates a local SQLite database file named `taskflow.db` if it does not already exist.

## Routes

- `/` - home page
- `/signup` - create an account
- `/login` - authenticate
- `/logout` - end the session

## Notes

- Passwords are stored as hashes using Werkzeug.
- Emails are normalized to lowercase.
- You can override the database path with `TASKFLOW_DATABASE`.
