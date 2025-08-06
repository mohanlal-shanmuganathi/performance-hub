import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_root():
    """Test root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print("Root endpoint:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def test_login():
    """Test login endpoint"""
    login_data = {
        "email": "admin@company.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"\nLogin endpoint: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Login successful!")
        print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"Role: {data['user']['role']}")
        return data['access_token']
    else:
        print("Login failed:", response.text)
        return None

def test_goals(token):
    """Test goals endpoint with authentication"""
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/goals", headers=headers)
    print(f"\nGoals endpoint: {response.status_code}")
    
    if response.status_code == 200:
        goals = response.json()
        print(f"Found {len(goals)} goals")
        for goal in goals:
            print(f"- {goal['title']} ({goal['status']}) - {goal['progress']}%")
    else:
        print("Goals request failed:", response.text)

if __name__ == "__main__":
    print("Testing Employee Performance Management API")
    print("=" * 50)
    
    try:
        # Test root endpoint
        test_root()
        
        # Test login
        token = test_login()
        
        # Test authenticated endpoint
        test_goals(token)
        
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the API server.")
        print("Make sure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"Error: {e}")