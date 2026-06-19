import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template_string, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

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
  <title>TaskFlow Auth</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
    nav a { margin-right: 1rem; }
    form { display: grid; gap: 0.75rem; max-width: 420px; }
    input { padding: 0.5rem; }
    .flash { padding: 0.75rem; background: #f2f2f2; border-left: 4px solid #666; margin: 1rem 0; }
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

  {{ content|safe }}
</body>
</html>
"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db



def init_db():
    db = get_db()
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


@app.teardown_appcontext
def close_db(_error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = None
    if user_id is not None:
        g.user = get_db().execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,)).fetchone()


@app.before_request
def ensure_db_initialized():
    init_db()



def render_page(content_template, **context):
    rendered_content = render_template_string(content_template, user=g.user, **context)
    return render_template_string(BASE_TEMPLATE, content=rendered_content, user=g.user)



def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Please log in to continue.')
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


@app.route('/')
def index():
    if g.user:
        content = '<h1>Welcome back, {{ user[\'name\'] }}!</h1><p>Your account session is active.</p>'
    else:
        content = '<h1>Welcome to TaskFlow</h1><p>Please sign up or log in to continue.</p>'
    return render_page(content)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        db = get_db()

        if not name:
            flash('Name is required.')
        elif not email:
            flash('Email is required.')
        elif not password:
            flash('Password is required.')
        elif len(password) < MIN_PASSWORD_LENGTH:
            flash(f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.')
        elif db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone() is not None:
            flash('An account with that email already exists.')
        else:
            cursor = db.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                (name, email, generate_password_hash(password))
            )
            db.commit()
            session.clear()
            session['user_id'] = cursor.lastrowid
            flash('Account created successfully.')
            return redirect(url_for('index'))

    content = """
    <h1>Sign up</h1>
    <form method="post">
      <label>Name <input type="text" name="name" required></label>
      <label>Email <input type="email" name="email" required></label>
      <label>Password <input type="password" name="password" required></label>
      <button type="submit">Create account</button>
    </form>
    <p>Minimum password length: {{ min_length }}</p>
    """
    return render_page(content, min_length=MIN_PASSWORD_LENGTH)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.')
        else:
            session.clear()
            session['user_id'] = user['id']
            flash('Logged in successfully.')
            return redirect(url_for('index'))

    content = """
    <h1>Log in</h1>
    <form method="post">
      <label>Email <input type="email" name="email" required></label>
      <label>Password <input type="password" name="password" required></label>
      <button type="submit">Log in</button>
    </form>
    """
    return render_page(content)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
