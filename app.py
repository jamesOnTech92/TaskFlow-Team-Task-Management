import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template_string, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'taskflow.db')
MIN_PASSWORD_LENGTH = 8

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['DATABASE'] = DATABASE

BASE_TEMPLATE = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>TaskFlow Accounts</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 760px; margin: 2rem auto; padding: 0 1rem; }
    nav { margin-bottom: 1.5rem; }
    nav a { margin-right: 1rem; }
    form { max-width: 420px; display: grid; gap: .75rem; }
    label { display: grid; gap: .25rem; }
    input { padding: .5rem; font-size: 1rem; }
    button { padding: .6rem .9rem; width: fit-content; }
    .flash { padding: .75rem 1rem; border-radius: 4px; margin-bottom: 1rem; }
    .flash.error { background: #fde8e8; color: #8a1c1c; }
    .flash.success { background: #e8f7ec; color: #176b34; }
  </style>
</head>
<body>
  <nav>
    <a href=\"{{ url_for('index') }}\">Home</a>
    {% if user %}
      <span>Signed in as {{ user['name'] }} ({{ user['email'] }})</span>
      <a href=\"{{ url_for('logout') }}\">Log out</a>
    {% else %}
      <a href=\"{{ url_for('signup') }}\">Sign up</a>
      <a href=\"{{ url_for('login') }}\">Log in</a>
    {% endif %}
  </nav>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        <div class=\"flash {{ category }}\">{{ message }}</div>
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
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            'SELECT id, name, email, password_hash FROM users WHERE id = ?',
            (user_id,),
        ).fetchone()


@app.teardown_appcontext
def close_db(_exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.context_processor
def inject_user():
    return {'user': getattr(g, 'user', None)}


def render_page(body, **context):
    return render_template_string(BASE_TEMPLATE, body=body, **context)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash('Please log in to access that page.', 'error')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view


@app.route('/')
def index():
    if g.user:
        body = """
        <h1>Welcome back, {{ user['name'] }}!</h1>
        <p>Your TaskFlow account session is active.</p>
        <p><a href=\"{{ url_for('logout') }}\">Log out</a></p>
        """
    else:
        body = """
        <h1>TaskFlow Accounts</h1>
        <p>Create an account or log in to continue.</p>
        <p><a href=\"{{ url_for('signup') }}\">Sign up</a> or <a href=\"{{ url_for('login') }}\">log in</a>.</p>
        """
    return render_page(body)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        error = None
        if not name:
            error = 'Name is required.'
        elif not email:
            error = 'Email is required.'
        elif len(password) < MIN_PASSWORD_LENGTH:
            error = f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.'
        else:
            db = get_db()
            existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
            if existing:
                error = 'An account with that email already exists.'
            else:
                cursor = db.execute(
                    'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                    (name, email, generate_password_hash(password)),
                )
                db.commit()
                session.clear()
                session['user_id'] = cursor.lastrowid
                flash('Account created successfully.', 'success')
                return redirect(url_for('index'))

        flash(error, 'error')

    body = f"""
    <h1>Sign up</h1>
    <form method=\"post\">
      <label>
        Name
        <input type=\"text\" name=\"name\" value=\"{{{{ request.form.get('name', '') }}}}\" required>
      </label>
      <label>
        Email
        <input type=\"email\" name=\"email\" value=\"{{{{ request.form.get('email', '') }}}}\" required>
      </label>
      <label>
        Password
        <input type=\"password\" name=\"password\" required>
      </label>
      <small>Minimum password length: {MIN_PASSWORD_LENGTH} characters.</small>
      <button type=\"submit\">Create account</button>
    </form>
    """
    return render_page(body)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = get_db().execute(
            'SELECT id, name, email, password_hash FROM users WHERE email = ?',
            (email,),
        ).fetchone()

        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
        else:
            session.clear()
            session['user_id'] = user['id']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))

    body = """
    <h1>Log in</h1>
    <form method=\"post\">
      <label>
        Email
        <input type=\"email\" name=\"email\" value=\"{{ request.form.get('email', '') }}\" required>
      </label>
      <label>
        Password
        <input type=\"password\" name=\"password\" required>
      </label>
      <button type=\"submit\">Log in</button>
    </form>
    """
    return render_page(body)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


init_db()

if __name__ == '__main__':
    app.run(debug=True)
