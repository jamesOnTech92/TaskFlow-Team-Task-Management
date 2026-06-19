import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template_string, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "taskflow.db")
MIN_PASSWORD_LENGTH = 8

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

try:
    from flask_session import Session

    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = os.path.join(BASE_DIR, ".flask_session")
    app.config["SESSION_PERMANENT"] = False
    os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)
    Session(app)
except Exception:
    pass

BASE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TaskFlow Auth</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
    nav a { margin-right: 1rem; }
    .flash { padding: 0.75rem 1rem; border-radius: 4px; margin: 1rem 0; }
    .flash.error { background: #ffe3e3; }
    .flash.success { background: #e3ffea; }
    form { display: grid; gap: 0.75rem; max-width: 420px; }
    label { display: grid; gap: 0.25rem; }
    input { padding: 0.5rem; }
    button { width: fit-content; padding: 0.6rem 1rem; }
  </style>
</head>
<body>
  <nav>
    <a href="{{ url_for('index') }}">Home</a>
    {% if g.user %}
      <span>Signed in as {{ g.user['name'] }}</span>
      <a href="{{ url_for('logout') }}">Log out</a>
    {% else %}
      <a href="{{ url_for('signup') }}">Sign up</a>
      <a href="{{ url_for('login') }}">Log in</a>
    {% endif %}
  </nav>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        <div class="flash {{ category }}">{{ message }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}

  {{ content|safe }}
</body>
</html>
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()
    db.close()


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.before_request
def ensure_db_initialized():
    init_db()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    if g.user:
        content = """
        <h1>Welcome back, {{ g.user['name'] }}!</h1>
        <p>You are authenticated in TaskFlow.</p>
        <p>Email: {{ g.user['email'] }}</p>
        """
    else:
        content = """
        <h1>TaskFlow Accounts</h1>
        <p>Create an account or sign in to continue.</p>
        """
    return render_template_string(BASE_TEMPLATE, content=render_template_string(content))


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
        elif not password:
            error = "Password is required."
        elif len(password) < MIN_PASSWORD_LENGTH:
            error = f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."

        db = get_db()
        if error is None:
            existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                error = "An account with that email already exists."

        if error is None:
            cursor = db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            db.commit()
            session.clear()
            session["user_id"] = cursor.lastrowid
            flash("Account created successfully.", "success")
            return redirect(url_for("index"))

        flash(error, "error")

    content = f"""
    <h1>Sign up</h1>
    <form method=\"post\">
      <label>Name<input type=\"text\" name=\"name\" required></label>
      <label>Email<input type=\"email\" name=\"email\" required></label>
      <label>Password<input type=\"password\" name=\"password\" minlength=\"{MIN_PASSWORD_LENGTH}\" required></label>
      <button type=\"submit\">Create account</button>
    </form>
    """
    return render_template_string(BASE_TEMPLATE, content=content)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        error = None

        user = get_db().execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Incorrect email or password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))

        flash(error, "error")

    content = """
    <h1>Log in</h1>
    <form method="post">
      <label>Email<input type="email" name="email" required></label>
      <label>Password<input type="password" name="password" required></label>
      <button type="submit">Log in</button>
    </form>
    """
    return render_template_string(BASE_TEMPLATE, content=content)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
