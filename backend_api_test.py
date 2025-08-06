import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000/api"

class APITester:
    def __init__(self):
        self.tokens = {}
        self.test_data = {}
        
    def login(self, email, password, role_name):
        """Login and store token"""
        print(f"\nTesting {role_name} Login...")
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.tokens[role_name] = data['access_token']
            print(f"SUCCESS: {role_name} login successful")
            return True
        else:
            print(f"FAILED: {role_name} login failed: {response.text}")
            return False
    
    def get_headers(self, role):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.tokens[role]}"}
    
    def test_employees_api(self):
        """Test all employee endpoints"""
        print("\nTesting Employee Management APIs...")
        
        # Test GET employees (admin)
        response = requests.get(f"{BASE_URL}/employees", headers=self.get_headers('admin'))
        if response.status_code == 200:
            print("SUCCESS: GET /employees (admin)")
            employees = response.json()
            if employees:
                self.test_data['employee_id'] = employees[0]['id']
        else:
            print(f"FAILED: GET /employees - {response.text}")
        
        # Test CREATE employee (admin)
        import time
        timestamp = int(time.time())
        new_employee = {
            "email": f"test.employee.{timestamp}@company.com",
            "password": "test123",
            "first_name": "Test",
            "last_name": "Employee",
            "role": "employee",
            "department": "Testing",
            "position": "Test Engineer",
            "hire_date": "2024-01-01"
        }
        
        response = requests.post(f"{BASE_URL}/employees", 
                               json=new_employee, 
                               headers=self.get_headers('admin'))
        if response.status_code == 201:
            print("SUCCESS: POST /employees (create)")
            self.test_data['new_employee_id'] = response.json()['id']
        else:
            print(f"FAILED: POST /employees - {response.text}")
        
        # Test GET single employee
        if 'employee_id' in self.test_data:
            response = requests.get(f"{BASE_URL}/employees/{self.test_data['employee_id']}", 
                                  headers=self.get_headers('admin'))
            if response.status_code == 200:
                print("SUCCESS: GET /employees/{id}")
            else:
                print(f"FAILED: GET /employees/{{id}} - {response.text}")
        
        # Test UPDATE employee
        if 'new_employee_id' in self.test_data:
            update_data = {"department": "Updated Testing"}
            response = requests.put(f"{BASE_URL}/employees/{self.test_data['new_employee_id']}", 
                                  json=update_data, 
                                  headers=self.get_headers('admin'))
            if response.status_code == 200:
                print("SUCCESS: PUT /employees/{id} (update)")
            else:
                print(f"FAILED: PUT /employees/{{id}} - {response.text}")
    
    def test_goals_api(self):
        """Test all goals endpoints"""
        print("\nTesting Goals Management APIs...")
        
        # Test GET goals
        response = requests.get(f"{BASE_URL}/goals", headers=self.get_headers('admin'))
        if response.status_code == 200:
            print("SUCCESS: GET /goals")
            goals = response.json()
            if goals:
                self.test_data['goal_id'] = goals[0]['id']
        else:
            print(f"FAILED: GET /goals - {response.text}")
        
        # Test CREATE goal
        new_goal = {
            "title": "Test Goal API",
            "description": "Testing goal creation via API",
            "category": "Technical Skills",
            "target_date": "2024-12-31",
            "progress": 0,
            "status": "draft"
        }
        
        response = requests.post(f"{BASE_URL}/goals", 
                               json=new_goal, 
                               headers=self.get_headers('employee'))
        if response.status_code == 201:
            print("SUCCESS: POST /goals (create)")
            self.test_data['new_goal_id'] = response.json()['id']
        else:
            print(f"FAILED: POST /goals - {response.text}")
        
        # Test UPDATE goal
        if 'new_goal_id' in self.test_data:
            update_data = {"progress": 50, "status": "active"}
            response = requests.put(f"{BASE_URL}/goals/{self.test_data['new_goal_id']}", 
                                  json=update_data, 
                                  headers=self.get_headers('employee'))
            if response.status_code == 200:
                print("SUCCESS: PUT /goals/{id} (update)")
            else:
                print(f"FAILED: PUT /goals/{{id}} - {response.text}")
        
        # Test APPROVE goal (manager)
        if 'new_goal_id' in self.test_data:
            response = requests.post(f"{BASE_URL}/goals/{self.test_data['new_goal_id']}/approve", 
                                   headers=self.get_headers('manager'))
            if response.status_code == 200:
                print("SUCCESS: POST /goals/{id}/approve")
            else:
                print(f"FAILED: POST /goals/{{id}}/approve - {response.text}")
    
    def test_reviews_api(self):
        """Test all reviews endpoints"""
        print("\nTesting Reviews APIs...")
        
        # Test GET reviews
        response = requests.get(f"{BASE_URL}/reviews", headers=self.get_headers('admin'))
        if response.status_code == 200:
            print("SUCCESS: GET /reviews")
            reviews = response.json()
            if reviews:
                self.test_data['review_id'] = reviews[0]['id']
        else:
            print(f"FAILED: GET /reviews - {response.text}")
        
        # Test CREATE review - use admin to review any employee
        if 'employee_id' in self.test_data:
            new_review = {
                "reviewee_id": self.test_data['employee_id'],
                "review_type": "manager",
                "review_period": "Q4 2024",
                "overall_rating": 4,
                "technical_skills": 4,
                "communication": 3,
                "leadership": 3,
                "teamwork": 4,
                "comments": "Good performance overall",
                "strengths": "Strong technical skills",
                "areas_for_improvement": "Communication skills"
            }
            
            response = requests.post(f"{BASE_URL}/reviews", 
                                   json=new_review, 
                                   headers=self.get_headers('admin'))
            if response.status_code == 201:
                print("SUCCESS: POST /reviews (create)")
                self.test_data['new_review_id'] = response.json()['id']
            else:
                print(f"FAILED: POST /reviews - {response.text}")
        
        # Test SUBMIT review
        if 'new_review_id' in self.test_data:
            response = requests.post(f"{BASE_URL}/reviews/{self.test_data['new_review_id']}/submit", 
                                   headers=self.get_headers('admin'))
            if response.status_code == 200:
                print("SUCCESS: POST /reviews/{id}/submit")
            else:
                print(f"FAILED: POST /reviews/{{id}}/submit - {response.text}")
    
    def test_skills_api(self):
        """Test all skills endpoints"""
        print("\nTesting Skills APIs...")
        
        # Test GET skills
        response = requests.get(f"{BASE_URL}/skills", headers=self.get_headers('admin'))
        if response.status_code == 200:
            print("SUCCESS: GET /skills")
        else:
            print(f"FAILED: GET /skills - {response.text}")
        
        # Test CREATE skill
        new_skill = {
            "skill_name": "API Testing",
            "proficiency_level": 3,
            "category": "Technical",
            "target_level": 4
        }
        
        response = requests.post(f"{BASE_URL}/skills", 
                               json=new_skill, 
                               headers=self.get_headers('employee'))
        if response.status_code == 201:
            print("SUCCESS: POST /skills (create)")
            self.test_data['new_skill_id'] = response.json()['id']
        else:
            print(f"FAILED: POST /skills - {response.text}")
    
    def test_analytics_api(self):
        """Test all analytics endpoints"""
        print("\nTesting Analytics APIs...")
        
        endpoints = [
            '/analytics/dashboard',
            '/analytics/performance-trends',
            '/analytics/team-comparison',
            '/analytics/skills-gap'
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=self.get_headers('admin'))
            if response.status_code == 200:
                print(f"SUCCESS: GET {endpoint}")
            else:
                print(f"FAILED: GET {endpoint} - {response.text}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("Starting Comprehensive API Testing...")
        
        # Login with different roles
        logins = [
            ("admin@company.com", "admin123", "admin"),
            ("manager@company.com", "manager123", "manager"),
            ("employee@company.com", "employee123", "employee")
        ]
        
        for email, password, role in logins:
            if not self.login(email, password, role):
                print(f"FAILED: Cannot continue testing without {role} login")
                return
        
        # Run all tests
        self.test_employees_api()
        self.test_goals_api()
        self.test_reviews_api()
        self.test_skills_api()
        self.test_analytics_api()
        
        print("\nAPI Testing Complete!")
        print(f"Test Data Created: {self.test_data}")

if __name__ == "__main__":
    try:
        tester = APITester()
        tester.run_all_tests()
    except requests.exceptions.ConnectionError:
        print("FAILED: Cannot connect to API server. Make sure Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"FAILED: Test failed with error: {e}")