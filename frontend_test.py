import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os

class FrontendTester:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except:
            print("Chrome driver not found, trying without headless mode...")
            chrome_options = Options()
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.wait = WebDriverWait(self.driver, 10)
        
    def test_login(self):
        """Test login functionality"""
        print("Testing login...")
        
        # Open the frontend
        file_path = os.path.abspath("working_modern_frontend.html")
        self.driver.get(f"file://{file_path}")
        
        # Wait for page to load
        time.sleep(2)
        
        # Find and fill login form
        email_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Clear and enter credentials
        email_input.clear()
        email_input.send_keys("admin@company.com")
        password_input.clear()
        password_input.send_keys("admin123")
        
        # Click login
        login_button.click()
        
        # Wait for dashboard to load
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Welcome back')]")))
            print("SUCCESS: Login successful")
            return True
        except:
            print("FAILED: Login failed")
            return False
    
    def test_employee_management(self):
        """Test employee add/edit functionality"""
        print("Testing employee management...")
        
        # Navigate to employees tab
        try:
            employees_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Team')]")))
            employees_tab.click()
            time.sleep(2)
            
            # Click Add Employee button
            add_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Employee')]")))
            add_button.click()
            time.sleep(1)
            
            # Fill employee form
            email_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            first_name_input = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")[0]
            last_name_input = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")[1]
            
            timestamp = str(int(time.time()))
            email_input.send_keys(f"test.frontend.{timestamp}@company.com")
            password_input.send_keys("test123")
            first_name_input.send_keys("Frontend")
            last_name_input.send_keys("Test")
            
            # Submit form
            create_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
            create_button.click()
            time.sleep(2)
            
            print("SUCCESS: Employee creation form submitted")
            return True
            
        except Exception as e:
            print(f"FAILED: Employee management test failed - {str(e)}")
            return False
    
    def test_goal_management(self):
        """Test goal add/edit functionality"""
        print("Testing goal management...")
        
        try:
            # Navigate to goals tab
            goals_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Goals')]")))
            goals_tab.click()
            time.sleep(2)
            
            # Click Create Goal button
            create_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Goal')]")))
            create_button.click()
            time.sleep(1)
            
            # Fill goal form
            title_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            description_textarea = self.driver.find_element(By.CSS_SELECTOR, "textarea")
            
            title_input.send_keys("Frontend Test Goal")
            description_textarea.send_keys("This is a test goal created from frontend")
            
            # Submit form
            create_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
            create_button.click()
            time.sleep(2)
            
            print("SUCCESS: Goal creation form submitted")
            return True
            
        except Exception as e:
            print(f"FAILED: Goal management test failed - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all frontend tests"""
        print("Starting Frontend Testing...")
        
        results = {
            'login': False,
            'employees': False,
            'goals': False
        }
        
        try:
            # Test login
            results['login'] = self.test_login()
            
            if results['login']:
                # Test employee management
                results['employees'] = self.test_employee_management()
                
                # Test goal management  
                results['goals'] = self.test_goal_management()
            
            print("\nFrontend Test Results:")
            print(f"Login: {'PASS' if results['login'] else 'FAIL'}")
            print(f"Employee Management: {'PASS' if results['employees'] else 'FAIL'}")
            print(f"Goal Management: {'PASS' if results['goals'] else 'FAIL'}")
            
        except Exception as e:
            print(f"Test failed with error: {e}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    try:
        tester = FrontendTester()
        tester.run_all_tests()
    except Exception as e:
        print(f"Failed to initialize frontend tester: {e}")
        print("Manual testing required - open working_modern_frontend.html in browser")