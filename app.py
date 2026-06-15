from __future__ import annotations

import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "taskflow.db"
MIN_PASSWORD_LENGTH = 8

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
    DATABASE=str(DATABASE),
    MIN_PASSWORD_LENGTH=MIN_PASSWORD_LENGTH,
)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(app.config["DATABASE"])
    try:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            """
        )
        db.commit()
    finally:
        db.close()


@app.before_request
def load_logged_in_user() -> None:
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        error = None

        if not name:
            error = "Name is required."
        elif not email:
            error = "Email is required."
        elif len(password) < app.config["MIN_PASSWORD_LENGTH"]:
            error = f"Password must be at least {app.config['MIN_PASSWORD_LENGTH']} characters."
        elif (
            get_db().execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            is not None
        ):
            error = "An account with that email already exists."

        if error is None:
            db = get_db()
            cursor = db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            db.commit()
            session.clear()
            session["user_id"] = cursor.lastrowid
            flash("Account created successfully.")
            return redirect(url_for("dashboard"))

        flash(error)

    return render_template("signup.html", min_password_length=app.config["MIN_PASSWORD_LENGTH"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash("Logged in successfully.")
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


init_db()


if __name__ == "__main__":
    app.run(debug=True)
