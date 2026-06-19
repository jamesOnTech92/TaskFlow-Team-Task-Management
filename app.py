import os
import sqlite3
from functools import wraps
from flask import Flask, g, redirect, render_template_string, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'taskflow.db')
MIN_PASSWORD_LENGTH = 8

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['DATABASE'] = DATABASE

BASE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }}</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
    nav { margin-bottom: 1rem; }
    nav a { margin-right: 1rem; }
    form { display: grid; gap: 0.75rem; max-width: 400px; }
    label { display: grid; gap: 0.25rem; }
    input { padding: 0.5rem; }
    button { width: fit-content; padding: 0.5rem 1rem; }
    .flash { padding: 0.75rem; background: #f3f4f6; border: 1px solid #d1d5db; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <nav>
    <a href="{{ url_for('index') }}">Home</a>
    {% if user %}
      <span>Signed in as {{ user['name'] }} ({{ user['email'] }})</span>
      <a href="{{ url_for('logout') }}">Log out</a>
    {% else %}
      <a href="{{ url_for('signup') }}">Sign up</a>
      <a href="{{ url_for('login') }}">Log in</a>
    {% endif %}
  </nav>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      {% for message in messages %}
        <div class="flash">{{ message }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}
  {{ body|safe }}
</body>
</html>
"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = sqlite3.connect(app.config['DATABASE'])
    try:
        db.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            '''
        )
        db.commit()
    finally:
        db.close()


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            'SELECT id, name, email FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def render_page(title, body):
    return render_template_string(BASE_TEMPLATE, title=title, body=body, user=g.user)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash('Please log in to continue.')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


@app.route('/')
def index():
    if g.user:
        body = f"<h1>Welcome back, {g.user['name']}!</h1><p>Your account is active and authenticated.</p>"
    else:
        body = '<h1>TaskFlow Accounts</h1><p>Create an account or log in to start using TaskFlow.</p>'
    return render_page('TaskFlow', body)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('Name, email, and password are required.')
        elif len(password) < MIN_PASSWORD_LENGTH:
            flash(f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.')
        else:
            db = get_db()
            existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
            if existing:
                flash('An account with that email already exists.')
            else:
                cursor = db.execute(
                    'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                    (name, email, generate_password_hash(password)),
                )
                db.commit()
                session.clear()
                session['user_id'] = cursor.lastrowid
                flash('Account created successfully.')
                return redirect(url_for('index'))

    body = f"""
    <h1>Sign up</h1>
    <form method="post">
      <label>Name<input type="text" name="name" required></label>
      <label>Email<input type="email" name="email" required></label>
      <label>Password<input type="password" name="password" required></label>
      <small>Minimum password length: {MIN_PASSWORD_LENGTH} characters.</small>
      <button type="submit">Create account</button>
    </form>
    """
    return render_page('Sign up', body)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = get_db().execute(
            'SELECT id, name, email, password_hash FROM users WHERE email = ?', (email,)
        ).fetchone()

        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.')
        else:
            session.clear()
            session['user_id'] = user['id']
            flash('Logged in successfully.')
            return redirect(url_for('index'))

    body = """
    <h1>Log in</h1>
    <form method="post">
      <label>Email<input type="email" name="email" required></label>
      <label>Password<input type="password" name="password" required></label>
      <button type="submit">Log in</button>
    </form>
    """
    return render_page('Log in', body)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('index'))


init_db()

if __name__ == '__main__':
    app.run(debug=True)
