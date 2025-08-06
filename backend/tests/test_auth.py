import pytest
import json
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Create test user
    user = User(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role='employee'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    # Login and get token
    response = client.post('/api/auth/login', 
                          data=json.dumps({
                              'email': 'test@example.com',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    token = json.loads(response.data)['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_login_success(client):
    # Create test user
    user = User(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role='employee'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/api/auth/login',
                          data=json.dumps({
                              'email': 'test@example.com',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'user' in data

def test_login_invalid_credentials(client):
    response = client.post('/api/auth/login',
                          data=json.dumps({
                              'email': 'nonexistent@example.com',
                              'password': 'wrongpassword'
                          }),
                          content_type='application/json')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid credentials'

def test_get_current_user(client, auth_headers):
    response = client.get('/api/auth/me', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['email'] == 'test@example.com'
    assert data['first_name'] == 'Test'