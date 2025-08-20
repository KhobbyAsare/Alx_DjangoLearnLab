#!/usr/bin/env python
"""
Comprehensive test script for Posts and Comments API functionality
"""

import requests
import json
import sys
import time
from datetime import datetime


class PostsAPITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.user_data = None
        self.created_post_id = None
        self.created_comment_id = None
    
    def print_response(self, response, title):
        """Print formatted response"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return response_data
        except:
            print(f"Response Text: {response.text}")
            return None
    
    def setup_authentication(self):
        """Set up authentication by registering and logging in a test user"""
        print("🔐 Setting up test authentication...")
        
        # Create unique username with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        username = f"testuser_{timestamp}"
        
        # Register user
        register_url = f"{self.base_url}/api/auth/register/"
        register_data = {
            "username": username,
            "email": f"{username}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "bio": "Test user for API testing",
            "password": "testpassword123",
            "password_confirm": "testpassword123"
        }
        
        response = requests.post(register_url, json=register_data, headers=self.headers)
        response_data = self.print_response(response, "USER REGISTRATION")
        
        if response.status_code == 201 and response_data:
            self.token = response_data.get('token')
            self.user_data = response_data.get('user')
            if self.token:
                self.headers["Authorization"] = f"Token {self.token}"
                print(f"✅ Authentication setup successful! Token: {self.token[:20]}...")
                return True
        
        print("❌ Authentication setup failed")
        return False
    
    def test_create_post(self):
        """Test creating a new post"""
        if not self.token:
            print("❌ No authentication token available")
            return False
        
        url = f"{self.base_url}/api/posts/"
        data = {
            "title": "My First Test Post",
            "content": "This is a test post created by the automated test script. It contains some sample content to test the post creation functionality.",
            "is_published": True
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        response_data = self.print_response(response, "CREATE POST TEST")
        
        if response.status_code == 201 and response_data:
            self.created_post_id = response_data.get('id')
            print(f"✅ Post created successfully! Post ID: {self.created_post_id}")
            return True
        
        print("❌ Post creation failed")
        return False
    
    def test_list_posts(self):
        """Test listing posts with pagination"""
        url = f"{self.base_url}/api/posts/"
        
        response = requests.get(url, headers=self.headers)
        response_data = self.print_response(response, "LIST POSTS TEST")
        
        if response.status_code == 200:
            print("✅ Posts listing successful!")
            return True
        
        print("❌ Posts listing failed")
        return False
    
    def test_retrieve_post(self):
        """Test retrieving a specific post"""
        if not self.created_post_id:
            print("❌ No post ID available for testing")
            return False
        
        url = f"{self.base_url}/api/posts/{self.created_post_id}/"
        
        response = requests.get(url, headers=self.headers)
        response_data = self.print_response(response, "RETRIEVE POST TEST")
        
        if response.status_code == 200:
            print("✅ Post retrieval successful!")
            return True
        
        print("❌ Post retrieval failed")
        return False
    
    def test_update_post(self):
        """Test updating a post"""
        if not self.created_post_id:
            print("❌ No post ID available for testing")
            return False
        
        url = f"{self.base_url}/api/posts/{self.created_post_id}/"
        data = {
            "title": "My Updated Test Post",
            "content": "This post has been updated by the test script. The content is now different from the original.",
            "is_published": True
        }
        
        response = requests.patch(url, json=data, headers=self.headers)
        response_data = self.print_response(response, "UPDATE POST TEST")
        
        if response.status_code == 200:
            print("✅ Post update successful!")
            return True
        
        print("❌ Post update failed")
        return False
    
    def test_create_comment(self):
        """Test creating a comment on a post"""
        if not self.created_post_id:
            print("❌ No post ID available for testing")
            return False
        
        url = f"{self.base_url}/api/comments/"
        data = {
            "content": "This is a test comment on the post. Great content!",
            "post": self.created_post_id
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        response_data = self.print_response(response, "CREATE COMMENT TEST")
        
        if response.status_code == 201 and response_data:
            self.created_comment_id = response_data.get('id')
            print(f"✅ Comment created successfully! Comment ID: {self.created_comment_id}")
            return True
        
        print("❌ Comment creation failed")
        return False
    
    def test_reply_to_comment(self):
        """Test replying to a comment"""
        if not self.created_comment_id:
            print("❌ No comment ID available for testing")
            return False
        
        url = f"{self.base_url}/api/comments/{self.created_comment_id}/reply/"
        data = {
            "content": "This is a reply to the comment above. Thanks for sharing!"
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        response_data = self.print_response(response, "REPLY TO COMMENT TEST")
        
        if response.status_code == 201:
            print("✅ Comment reply successful!")
            return True
        
        print("❌ Comment reply failed")
        return False
    
    def test_list_comments(self):
        """Test listing comments"""
        url = f"{self.base_url}/api/comments/"
        
        response = requests.get(url, headers=self.headers)
        response_data = self.print_response(response, "LIST COMMENTS TEST")
        
        if response.status_code == 200:
            print("✅ Comments listing successful!")
            return True
        
        print("❌ Comments listing failed")
        return False
    
    def test_my_posts(self):
        """Test getting current user's posts"""
        url = f"{self.base_url}/api/posts/my_posts/"
        
        response = requests.get(url, headers=self.headers)
        response_data = self.print_response(response, "MY POSTS TEST")
        
        if response.status_code == 200:
            print("✅ My posts retrieval successful!")
            return True
        
        print("❌ My posts retrieval failed")
        return False
    
    def test_post_search(self):
        """Test post search functionality"""
        url = f"{self.base_url}/api/posts/"
        params = {"search": "test"}
        
        response = requests.get(url, headers=self.headers, params=params)
        response_data = self.print_response(response, "POST SEARCH TEST")
        
        if response.status_code == 200:
            print("✅ Post search successful!")
            return True
        
        print("❌ Post search failed")
        return False
    
    def test_toggle_post_publish(self):
        """Test toggling post publish status"""
        if not self.created_post_id:
            print("❌ No post ID available for testing")
            return False
        
        url = f"{self.base_url}/api/posts/{self.created_post_id}/toggle_publish/"
        
        response = requests.post(url, headers=self.headers)
        response_data = self.print_response(response, "TOGGLE PUBLISH STATUS TEST")
        
        if response.status_code == 200:
            print("✅ Toggle publish status successful!")
            return True
        
        print("❌ Toggle publish status failed")
        return False
    
    def test_post_comments_endpoint(self):
        """Test getting comments for a specific post"""
        if not self.created_post_id:
            print("❌ No post ID available for testing")
            return False
        
        url = f"{self.base_url}/api/posts/{self.created_post_id}/comments/"
        
        response = requests.get(url, headers=self.headers)
        response_data = self.print_response(response, "POST COMMENTS ENDPOINT TEST")
        
        if response.status_code == 200:
            print("✅ Post comments endpoint successful!")
            return True
        
        print("❌ Post comments endpoint failed")
        return False
    
    def cleanup(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete created post (this will also delete associated comments)
        if self.created_post_id:
            url = f"{self.base_url}/api/posts/{self.created_post_id}/"
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 204:
                print("✅ Test post deleted successfully")
            else:
                print(f"⚠️ Failed to delete test post: {response.status_code}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Posts and Comments API Tests...")
        print(f"Base URL: {self.base_url}")
        
        tests = [
            ("Authentication Setup", self.setup_authentication),
            ("Create Post", self.test_create_post),
            ("List Posts", self.test_list_posts),
            ("Retrieve Post", self.test_retrieve_post),
            ("Update Post", self.test_update_post),
            ("Create Comment", self.test_create_comment),
            ("Reply to Comment", self.test_reply_to_comment),
            ("List Comments", self.test_list_comments),
            ("My Posts", self.test_my_posts),
            ("Post Search", self.test_post_search),
            ("Toggle Publish Status", self.test_toggle_post_publish),
            ("Post Comments Endpoint", self.test_post_comments_endpoint),
        ]
        
        tests_passed = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            if test_func():
                tests_passed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Cleanup
        self.cleanup()
        
        # Summary
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests Passed: {tests_passed}/{total_tests}")
        print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Your Posts and Comments API is working correctly!")
        else:
            print("❌ Some tests failed. Please check the error messages above.")
        
        return tests_passed == total_tests


if __name__ == "__main__":
    tester = PostsAPITester()
    
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
