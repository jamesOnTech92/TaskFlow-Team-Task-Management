import requests

def test_signup():
    response = requests.post('http://localhost:5000/signup', json={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'password123'
    })
    print('Signup:', response.status_code, response.json())

def test_login():
    response = requests.post('http://localhost:5000/login', json={
        'email': 'john@example.com',
        'password': 'password123'
    })
    print('Login:', response.status_code, response.json())

def test_logout():
    response = requests.post('http://localhost:5000/logout')
    print('Logout:', response.status_code, response.json())

if __name__ == '__main__':
    test_signup()
    test_login()
    test_logout()