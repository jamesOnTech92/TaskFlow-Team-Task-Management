import os
import sqlite3
from flask import Flask, flash, g, redirect, render_template_string, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(BASE_DIR, 'taskflow.db')
MIN_PASSWORD_LENGTH = 8

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['DATABASE'] = os.environ.get('TASKFLOW_DATABASE', DEFAULT_DB)

HOME_TEMPLATE = '''
<!doctype html>
<title>TaskFlow</title>
<h1>TaskFlow Accounts</h1>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul>{% for message in messages %}<li>{{ message }}</li>{% endfor %}</ul>
  {% endif %}
{% endwith %}
{% if user %}
  <p>Signed in as <strong>{{ user['name'] }}</strong> ({{ user['email'] }})</p>
  <p><a href="{{ url_for('logout') }}">Log out</a></p>
{% else %}
  <p><a href="{{ url_for('signup') }}">Sign up</a> | <a href="{{ url_for('login') }}">Log in</a></p>
{% endif %}
'''

AUTH_TEMPLATE = '''
<!doctype html>
<title>{{ title }}</title>
<h1>{{ title }}</h1>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul>{% for message in messages %}<li>{{ message }}</li>{% endfor %}</ul>
  {% endif %}
{% endwith %}
<form method="post">
  {% if signup %}
  <p><label>Name <input name="name" value="{{ request.form.get('name', '') }}" required></label></p>
  {% endif %}
  <p><label>Email <input type="email" name="email" value="{{ request.form.get('email', '') }}" required></label></p>
  <p><label>Password <input type="password" name="password" required></label></p>
  <button type="submit">{{ title }}</button>
</form>
<p><a href="{{ url_for('index') }}">Home</a></p>
'''


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(app.config['DATABASE'])
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
def teardown_db(exception):
    close_db(exception)


@app.route('/')
def index():
    return render_template_string(HOME_TEMPLATE, user=g.user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
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
        elif get_db().execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone() is not None:
            error = 'An account with that email already exists.'

        if error is None:
            db = get_db()
            cursor = db.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                (name, email, generate_password_hash(password)),
            )
            db.commit()
            session.clear()
            session['user_id'] = cursor.lastrowid
            flash('Account created successfully.')
            return redirect(url_for('index'))

        flash(error)

    return render_template_string(AUTH_TEMPLATE, title='Sign up', signup=True)


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

    return render_template_string(AUTH_TEMPLATE, title='Log in', signup=False)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('index'))


init_db()

if __name__ == '__main__':
    app.run(debug=True)
