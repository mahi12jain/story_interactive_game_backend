#!/usr/bin/env python3
"""
Interactive Story Platform API Tester
=====================================
This script tests all the APIs of your text-based game backend.
Run this after starting your FastAPI server to test all endpoints.

Usage:
    python test_apis.py

Make sure your FastAPI server is running on http://localhost:8000
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

class StoryPlatformTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.test_data = {}
        
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name: str, method: str, endpoint: str):
        """Print test information"""
        print(f"\n🧪 Testing: {test_name}")
        print(f"   Method: {method}")
        print(f"   Endpoint: {endpoint}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def print_response(self, response: requests.Response, expected_status: int = 200):
        """Print response information"""
        if not response:
            return False
            
        print(f"   Status: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"   Response: {json.dumps(response_json, indent=2)[:500]}...")
        except:
            print(f"   Response: {response.text[:200]}...")
        
        success = response.status_code == expected_status
        print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
        
        return success, response_json if success else None
    
    def test_server_health(self):
        """Test if server is running"""
        self.print_section("SERVER HEALTH CHECK")
        self.print_test("Server Health", "GET", "/")
        
        response = self.make_request("GET", "/")
        success, data = self.print_response(response)
        
        if not success:
            print("❌ Server is not running or accessible!")
            print("   Make sure your FastAPI server is running on http://localhost:8000")
            return False
        
        return True
    
    def test_authentication(self):
        """Test user registration and login"""
        self.print_section("AUTHENTICATION TESTS")
        
        # Test User Registration
        self.print_test("User Registration", "POST", "/auth/register")
        
        timestamp = int(time.time())
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "testpassword123"
        }
        
        response = self.make_request("POST", "/auth/register", user_data)
        success, data = self.print_response(response, 201)
        
        if success:
            self.test_data["user"] = data
            print(f"   ✅ User created with ID: {data.get('user_id')}")
        
        # Test User Login
        self.print_test("User Login", "POST", "/auth/login")
        
        login_data = {
            "username": user_data["email"],  # FastAPI OAuth2 uses username field for email
            "password": user_data["password"]
        }
        
        # For OAuth2PasswordRequestForm, we need to send as form data
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data=login_data,  # Use data instead of json for form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        success, data = self.print_response(response)
        
        if success:
            self.access_token = data.get("access_token")
            print(f"   ✅ Login successful, token obtained")
        
        # Test Protected Route
        if self.access_token:
            self.print_test("Get Current User", "GET", "/auth/me")
            response = self.make_request("GET", "/auth/me")
            success, data = self.print_response(response)
            
            if success:
                print(f"   ✅ Protected route accessible")
    
    def test_story_management(self):
        """Test story CRUD operations"""
        self.print_section("STORY MANAGEMENT TESTS")
        
        # Create Story
        self.print_test("Create Story", "POST", "/story/stories")
        
        story_data = {
            "title": f"Test Adventure {int(time.time())}",
            "description": "An epic test adventure to validate our APIs",
            "author": "API Tester",
            "difficulty_level": "medium",
            "category": "fantasy",
            "is_published": True,
            "created_at": datetime.now().isoformat()
        }
        
        response = self.make_request("POST", "/story/stories", story_data)
        success, data = self.print_response(response, 201)
        
        if success:
            self.test_data["story"] = data
            story_id = data.get("story_id")
            print(f"   ✅ Story created with ID: {story_id}")
        
        # Get All Stories
        self.print_test("Get All Stories", "GET", "/story/get_story")
        response = self.make_request("GET", "/story/get_story", params={"skip": 0, "limit": 10})
        success, data = self.print_response(response)
        
        # Get Story by ID
        if "story" in self.test_data:
            story_id = self.test_data["story"]["story_id"]
            self.print_test("Get Story by ID", "GET", f"/story/get_story/{story_id}")
            response = self.make_request("GET", f"/story/get_story/{story_id}")
            success, data = self.print_response(response)
        
        # Get Categories
        self.print_test("Get Categories", "GET", "/story/stories/categories")
        response = self.make_request("GET", "/story/stories/categories")
        success, data = self.print_response(response)
        
        # Update Story
        if "story" in self.test_data:
            story_id = self.test_data["story"]["story_id"]
            self.print_test("Update Story", "PUT", f"/story/stories/{story_id}")
            
            update_data = {
                "description": "Updated description for testing",
                "difficulty_level": "hard"
            }
            
            response = self.make_request("PUT", f"/story/stories/{story_id}", update_data)
            success, data = self.print_response(response)
    
    def test_story_nodes(self):
        """Test story node operations"""
        self.print_section("STORY NODES TESTS")
        
        if "story" not in self.test_data:
            print("❌ No story available for node testing. Skipping...")
            return
        
        story_id = self.test_data["story"]["story_id"]
        
        # Create Starting Node
        self.print_test("Create Starting Node", "POST", "/story-nodes/")
        
        start_node_data = {
            "story_id": story_id,
            "node_title": "The Beginning",
            "content": "You find yourself at the entrance of a dark cave. The air is thick with mystery and adventure awaits within.",
            "is_starting_node": True,
            "is_ending_node": False,
            "node_type": "story"
        }
        
        response = self.make_request("POST", "/story-nodes/", start_node_data)
        success, data = self.print_response(response, 201)
        
        if success:
            self.test_data["start_node"] = data
            print(f"   ✅ Starting node created with ID: {data.get('node_id')}")
        
        # Create Choice Node
        self.print_test("Create Choice Node", "POST", "/story-nodes/")
        
        choice_node_data = {
            "story_id": story_id,
            "node_title": "The Fork in the Path",
            "content": "You've ventured deeper into the cave and come across a fork in the path. Which way do you choose?",
            "is_starting_node": False,
            "is_ending_node": False,
            "node_type": "choice"
        }
        
        response = self.make_request("POST", "/story-nodes/", choice_node_data)
        success, data = self.print_response(response, 201)
        
        if success:
            self.test_data["choice_node"] = data
        
        # Create Ending Node
        self.print_test("Create Ending Node", "POST", "/story-nodes/")
        
        end_node_data = {
            "story_id": story_id,
            "node_title": "Victory!",
            "content": "Congratulations! You have successfully navigated through the cave and found the legendary treasure!",
            "is_starting_node": False,
            "is_ending_node": True,
            "node_type": "ending"
        }
        
        response = self.make_request("POST", "/story-nodes/", end_node_data)
        success, data = self.print_response(response, 201)
        
        if success:
            self.test_data["end_node"] = data
        
        # Get All Nodes for Story
        self.print_test("Get Story Nodes", "GET", f"/story-nodes/story/{story_id}")
        response = self.make_request("GET", f"/story-nodes/story/{story_id}")
        success, data = self.print_response(response)
        
        # Get Starting Node
        self.print_test("Get Starting Node", "GET", f"/story-nodes/story/{story_id}/starting-node")
        response = self.make_request("GET", f"/story-nodes/story/{story_id}/starting-node")
        success, data = self.print_response(response)
    
    def test_choices(self):
        """Test choice creation and management"""
        self.print_section("CHOICES TESTS")
        
        if "start_node" not in self.test_data or "choice_node" not in self.test_data:
            print("❌ Required nodes not available for choice testing. Skipping...")
            return
        
        start_node_id = self.test_data["start_node"]["node_id"]
        choice_node_id = self.test_data["choice_node"]["node_id"]
        end_node_id = self.test_data.get("end_node", {}).get("node_id")
        
        # Create Choice from Start to Choice Node
        self.print_test("Create Choice", "POST", "/choices/")
        
        choice_data = {
            "from_node_id": start_node_id,
            "to_node_id": choice_node_id,
            "choice_text": "Enter the cave cautiously",
            "choice_letter": "A",
            "consequences": "You proceed carefully into the darkness."
        }
        
        response = self.make_request("POST", "/choices/", choice_data)
        success, data = self.print_response(response, 201)
        
        if success:
            self.test_data["choice1"] = data
        
        # Create another choice if end node exists
        if end_node_id:
            choice_data2 = {
                "from_node_id": choice_node_id,
                "to_node_id": end_node_id,
                "choice_text": "Take the left path",
                "choice_letter": "A",
                "consequences": "The left path leads to treasure!"
            }
            
            response = self.make_request("POST", "/choices/", choice_data2)
            success, data = self.print_response(response, 201)
            
            if success:
                self.test_data["choice2"] = data
        
        # Get Choices for Node
        self.print_test("Get Node Choices", "GET", f"/choices/node/{start_node_id}")
        response = self.make_request("GET", f"/choices/node/{start_node_id}")
        success, data = self.print_response(response)
    
    def test_game_engine(self):
        """Test game engine functionality"""
        self.print_section("GAME ENGINE TESTS")
        
        if "story" not in self.test_data:
            print("❌ No story available for game engine testing. Skipping...")
            return
        
        story_id = self.test_data["story"]["story_id"]
        
        # Start Story
        self.print_test("Start Story", "POST", f"/game/start/{story_id}")
        response = self.make_request("POST", f"/game/start/{story_id}")
        success, data = self.print_response(response)
        
        if success:
            self.test_data["current_node"] = data
            print(f"   ✅ Story started at node: {data.get('node_title')}")
        
        # Make a Choice (if choices available)
        if "current_node" in self.test_data and self.test_data["current_node"].get("choices"):
            choices = self.test_data["current_node"]["choices"]
            if choices:
                choice = choices[0]
                current_node_id = self.test_data["current_node"]["node_id"]
                
                self.print_test("Make Choice", "POST", "/game/choice")
                
                choice_request = {
                    "choice_id": choice["choice_id"],
                    "current_node_id": current_node_id,
                    "user_id": self.test_data.get("user", {}).get("user_id")
                }
                
                response = self.make_request("POST", "/game/choice", choice_request)
                success, data = self.print_response(response)
                
                if success:
                    print(f"   ✅ Choice made, next node: {data.get('next_node', {}).get('node_title')}")
        
        # Get Current Node (for logged-in user)
        if self.access_token:
            self.print_test("Get Current Node", "GET", f"/game/current/{story_id}")
            response = self.make_request("GET", f"/game/current/{story_id}")
            success, data = self.print_response(response)
    
    def test_error_cases(self):
        """Test error handling"""
        self.print_section("ERROR HANDLING TESTS")
        
        # Test 404 errors
        self.print_test("Get Non-existent Story", "GET", "/story/get_story/99999")
        response = self.make_request("GET", "/story/get_story/99999")
        success, data = self.print_response(response, 404)
        
        # Test unauthorized access
        old_token = self.access_token
        self.access_token = "invalid_token"
        
        self.print_test("Unauthorized Access", "GET", "/auth/me")
        response = self.make_request("GET", "/auth/me")
        success, data = self.print_response(response, 401)
        
        self.access_token = old_token  # Restore valid token
        
        # Test duplicate user registration
        self.print_test("Duplicate User Registration", "POST", "/auth/register")
        if "user" in self.test_data:
            duplicate_user = {
                "username": "duplicate_user",
                "email": self.test_data["user"]["email"],  # Same email
                "password": "password123"
            }
            
            response = self.make_request("POST", "/auth/register", duplicate_user)
            success, data = self.print_response(response, 400)
    
    def cleanup_test_data(self):
        """Clean up test data (optional)"""
        self.print_section("CLEANUP (Optional)")
        
        # Delete test story if needed
        if "story" in self.test_data:
            story_id = self.test_data["story"]["story_id"]
            self.print_test("Delete Test Story", "DELETE", f"/story/stories/{story_id}")
            response = self.make_request("DELETE", f"/story/stories/{story_id}")
            success, data = self.print_response(response)
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Interactive Story Platform API Tests")
        print(f"   Base URL: {self.base_url}")
        print(f"   Timestamp: {datetime.now()}")
        
        # Check if server is running
        if not self.test_server_health():
            return
        
        # Run all test suites
        test_suites = [
            self.test_authentication,
            self.test_story_management,
            self.test_story_nodes,
            self.test_choices,
            self.test_game_engine,
            self.test_error_cases,
        ]
        
        for test_suite in test_suites:
            try:
                test_suite()
            except Exception as e:
                print(f"❌ Test suite failed: {e}")
        
        # Optional cleanup
        # self.cleanup_test_data()
        
        self.print_section("TEST SUMMARY")
        print("✅ All tests completed!")
        print("📝 Check the output above for detailed results")
        print("🔍 Look for ❌ FAIL markers to identify issues")

def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Interactive Story Platform APIs")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API server")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    tester = StoryPlatformTester(args.url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()