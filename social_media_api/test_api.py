#!/usr/bin/env python
"""
Test script for Social Media API endpoints
"""

import requests
import json
import sys


class APITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def print_response(self, response, title):
        """Print formatted response"""
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response Text: {response.text}")
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = f"{self.base_url}/api/auth/register/"
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "bio": "This is a test user",
            "password": "testpassword123",
            "password_confirm": "testpassword123"
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        self.print_response(response, "USER REGISTRATION TEST")
        
        if response.status_code == 201:
            response_data = response.json()
            self.token = response_data.get('token')
            if self.token:
                self.headers["Authorization"] = f"Token {self.token}"
                print(f"✅ Registration successful! Token saved: {self.token[:20]}...")
            else:
                print("❌ No token returned")
        else:
            print("❌ Registration failed")
        
        return response.status_code == 201
    
    def test_user_login(self):
        """Test user login endpoint"""
        url = f"{self.base_url}/api/auth/login/"
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        self.print_response(response, "USER LOGIN TEST")
        
        if response.status_code == 200:
            response_data = response.json()
            token = response_data.get('token')
            if token:
                print(f"✅ Login successful! Token: {token[:20]}...")
                return True
        
        print("❌ Login failed")
        return False
    
    def test_profile_view(self):
        """Test profile view endpoint"""
        if not self.token:
            print("❌ No token available for profile test")
            return False
        
        url = f"{self.base_url}/api/auth/profile/"
        response = requests.get(url, headers=self.headers)
        self.print_response(response, "PROFILE VIEW TEST")
        
        if response.status_code == 200:
            print("✅ Profile view successful!")
            return True
        
        print("❌ Profile view failed")
        return False
    
    def test_profile_update(self):
        """Test profile update endpoint"""
        if not self.token:
            print("❌ No token available for profile update test")
            return False
        
        url = f"{self.base_url}/api/auth/profile/"
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio for test user"
        }
        
        response = requests.patch(url, json=data, headers=self.headers)
        self.print_response(response, "PROFILE UPDATE TEST")
        
        if response.status_code == 200:
            print("✅ Profile update successful!")
            return True
        
        print("❌ Profile update failed")
        return False
    
    def test_user_list(self):
        """Test user list endpoint"""
        if not self.token:
            print("❌ No token available for user list test")
            return False
        
        url = f"{self.base_url}/api/auth/users/"
        response = requests.get(url, headers=self.headers)
        self.print_response(response, "USER LIST TEST")
        
        if response.status_code == 200:
            print("✅ User list successful!")
            return True
        
        print("❌ User list failed")
        return False
    
    def test_logout(self):
        """Test logout endpoint"""
        if not self.token:
            print("❌ No token available for logout test")
            return False
        
        url = f"{self.base_url}/api/auth/logout/"
        response = requests.post(url, headers=self.headers)
        self.print_response(response, "LOGOUT TEST")
        
        if response.status_code == 200:
            print("✅ Logout successful!")
            return True
        
        print("❌ Logout failed")
        return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Social Media API Tests...")
        print(f"Base URL: {self.base_url}")
        
        tests_passed = 0
        total_tests = 6
        
        # Test registration
        if self.test_user_registration():
            tests_passed += 1
        
        # Test login (with new user)
        if self.test_user_login():
            tests_passed += 1
        
        # Test profile view
        if self.test_profile_view():
            tests_passed += 1
        
        # Test profile update
        if self.test_profile_update():
            tests_passed += 1
        
        # Test user list
        if self.test_user_list():
            tests_passed += 1
        
        # Test logout
        if self.test_logout():
            tests_passed += 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests Passed: {tests_passed}/{total_tests}")
        print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Your API is working correctly!")
        else:
            print("❌ Some tests failed. Please check the error messages above.")
        
        return tests_passed == total_tests


if __name__ == "__main__":
    tester = APITester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the Django development server is running at http://127.0.0.1:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)
