# TaskFlow - Accounts and Authentication

This application includes the following features:
- **Sign Up**: Users can register using their name, email, and password. The password must be at least 8 characters long.
- **Log In**: Registered users can log in with their email and password.
- **Log Out**: Users can log out, clearing their session.
- **Dashboard**: Authenticated users can access a personalized dashboard.
- **Server-Side Sessions**: User sessions are managed securely.
- **SQLite Integration**: User data is stored in an SQLite database.

## Installation and Setup

1. Install dependencies:
   ```sh
   pip install flask werkzeug
   ```

2. Run the application:
   ```sh
   python app.py
   ```

3. Navigate to the following pages:
   - `/signup`: Register a new user.
   - `/login`: Log in to access your dashboard.
   - `/logout`: Log out of the application.
   - `/dashboard`: Access the authenticated user dashboard.

The database will automatically initialize upon application startup.

## File Structure
- `app.py`: Core Flask application.
- `templates/signup.html`: HTML template for user sign-up.
- `templates/login.html`: HTML template for user login.

Enjoy using TaskFlow for managing user authentication!