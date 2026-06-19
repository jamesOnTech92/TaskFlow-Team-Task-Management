# TaskFlow Accounts and Authentication

This repository contains a focused Flask + SQLite implementation of the TaskFlow accounts and authentication feature.

## Features

- Sign up with name, email, and password
- Log in with email and password
- Log out
- Server-side authenticated session flow using Flask sessions
- SQLite `users` table with:
  - `name`
  - `email`
  - `password_hash`
- Minimum password length rule: 8 characters
- Password hashing via Werkzeug

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

The app will create `taskflow.db` automatically on first use.

## Routes

- `/` — home page
- `/signup` — create an account
- `/login` — log in
- `/logout` — log out

## Notes

- Email addresses are stored in lowercase to avoid duplicate accounts with different casing.
- Passwords are never stored in plain text; only password hashes are stored.
- The default Flask secret key in `app.py` is for development only. Set `SECRET_KEY` in the environment for real deployments.
