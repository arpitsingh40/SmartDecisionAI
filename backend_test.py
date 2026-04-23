#!/usr/bin/env python3
"""
Backend API Testing for Smart Decision AI
Tests all CRUD operations and AI integration endpoints
"""
import requests
import sys
import json
import time
from datetime import datetime

class SmartDecisionAPITester:
    def __init__(self, base_url="https://decide-pro-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.guest_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.decision_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=120):
        """Run a single API test with extended timeout for AI calls"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    resp_data = response.json()
                    if isinstance(resp_data, dict) and len(str(resp_data)) < 500:
                        print(f"   Response: {resp_data}")
                    return True, resp_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout}s")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_guest_session(self):
        """Test guest session creation"""
        success, response = self.run_test("Guest Session Creation", "POST", "guest/session", 200)
        if success and 'guest_id' in response:
            self.guest_id = response['guest_id']
            print(f"   Guest ID: {self.guest_id}")
            return True
        return False

    def test_status_endpoints(self):
        """Test status check endpoints"""
        # Create status check
        test_data = {"client_name": f"test_client_{int(time.time())}"}
        success1, _ = self.run_test("Create Status Check", "POST", "status", 200, data=test_data)
        
        # Get status checks
        success2, _ = self.run_test("Get Status Checks", "GET", "status", 200)
        
        return success1 and success2

    def test_followups_generation(self):
        """Test AI follow-up questions generation"""
        test_decision = "Should I accept the software engineering job at Google or continue my PhD in Computer Science?"
        
        success, response = self.run_test(
            "AI Follow-ups Generation", 
            "POST", 
            "decisions/followups", 
            200, 
            data={"decision": test_decision},
            timeout=90  # AI calls can take time
        )
        
        if success and 'questions' in response:
            questions = response['questions']
            print(f"   Generated {len(questions)} questions")
            
            # Validate question structure
            for i, q in enumerate(questions):
                required_fields = ['id', 'question', 'type']
                missing = [f for f in required_fields if f not in q]
                if missing:
                    print(f"   ❌ Question {i+1} missing fields: {missing}")
                    return False
                
                # Check question types
                if q['type'] not in ['text', 'single_choice', 'multi_choice', 'slider']:
                    print(f"   ❌ Invalid question type: {q['type']}")
                    return False
                    
                # Validate choice questions have options
                if q['type'] in ['single_choice', 'multi_choice']:
                    if 'options' not in q or not q['options'] or len(q['options']) < 2:
                        print(f"   ❌ Choice question missing valid options")
                        return False
                        
                # Validate slider questions have min/max
                if q['type'] == 'slider':
                    if 'min' not in q or 'max' not in q:
                        print(f"   ❌ Slider question missing min/max")
                        return False
            
            print(f"   ✅ All {len(questions)} questions properly structured")
            return True
        return False

    def test_decision_analysis(self):
        """Test AI decision analysis"""
        test_decision = "Should I accept the software engineering job at Google or continue my PhD in Computer Science?"
        test_answers = [
            {"question": "What is your primary career goal?", "type": "single_choice", "answer": "Industry leadership"},
            {"question": "How important is financial stability?", "type": "slider", "answer": 8},
            {"question": "What are your key interests?", "type": "multi_choice", "answer": ["Technology", "Research"]},
            {"question": "Any other considerations?", "type": "text", "answer": "I want to make an impact"}
        ]
        
        success, response = self.run_test(
            "AI Decision Analysis", 
            "POST", 
            "decisions/analyze", 
            200, 
            data={"decision": test_decision, "answers": test_answers},
            timeout=90  # AI calls can take time
        )
        
        if success and 'options' in response:
            options = response['options']
            print(f"   Generated {len(options)} options")
            
            # Validate response structure
            required_fields = ['options', 'best_option_id', 'reasoning', 'confidence']
            missing = [f for f in required_fields if f not in response]
            if missing:
                print(f"   ❌ Response missing fields: {missing}")
                return False
            
            # Validate options
            if len(options) < 3 or len(options) > 5:
                print(f"   ❌ Expected 3-5 options, got {len(options)}")
                return False
                
            for i, option in enumerate(options):
                option_fields = ['id', 'title', 'description', 'pros', 'cons', 'risk_level', 'score']
                missing = [f for f in option_fields if f not in option]
                if missing:
                    print(f"   ❌ Option {i+1} missing fields: {missing}")
                    return False
                    
                # Validate score range
                if not (0 <= option['score'] <= 100):
                    print(f"   ❌ Option {i+1} score out of range: {option['score']}")
                    return False
                    
                # Validate risk level
                if option['risk_level'] not in ['Low', 'Medium', 'High']:
                    print(f"   ❌ Invalid risk level: {option['risk_level']}")
                    return False
            
            # Validate best option exists
            best_id = response['best_option_id']
            if not any(o['id'] == best_id for o in options):
                print(f"   ❌ Best option ID not found in options: {best_id}")
                return False
                
            # Validate confidence range
            if not (0 <= response['confidence'] <= 100):
                print(f"   ❌ Confidence out of range: {response['confidence']}")
                return False
            
            print(f"   ✅ Analysis properly structured with {len(options)} options")
            return True
        return False

    def test_save_decision(self):
        """Test saving a decision"""
        if not self.guest_id:
            print("   ❌ No guest_id available for save test")
            return False
            
        test_data = {
            "guest_id": self.guest_id,
            "title": "Test Decision",
            "decision": "Should I test this API?",
            "answers": [{"question": "Test question?", "type": "text", "answer": "Yes"}],
            "result": {
                "options": [
                    {
                        "id": "opt_1",
                        "title": "Test Option",
                        "description": "A test option",
                        "pros": ["Pro 1", "Pro 2"],
                        "cons": ["Con 1", "Con 2"],
                        "risk_level": "Low",
                        "short_term_outcome": "Good",
                        "long_term_outcome": "Better",
                        "score": 85
                    }
                ],
                "best_option_id": "opt_1",
                "reasoning": "Test reasoning",
                "confidence": 90
            }
        }
        
        success, response = self.run_test("Save Decision", "POST", "decisions", 200, data=test_data)
        if success and 'id' in response:
            self.decision_id = response['id']
            print(f"   Decision ID: {self.decision_id}")
            return True
        return False

    def test_list_decisions(self):
        """Test listing decisions"""
        if not self.guest_id:
            print("   ❌ No guest_id available for list test")
            return False
            
        success, response = self.run_test(
            "List Decisions", 
            "GET", 
            "decisions", 
            200, 
            params={"guest_id": self.guest_id}
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} decisions")
            return True
        return False

    def test_get_decision(self):
        """Test getting a specific decision"""
        if not self.guest_id or not self.decision_id:
            print("   ❌ No guest_id or decision_id available for get test")
            return False
            
        success, response = self.run_test(
            "Get Decision", 
            "GET", 
            f"decisions/{self.decision_id}", 
            200, 
            params={"guest_id": self.guest_id}
        )
        
        if success and 'id' in response and response['id'] == self.decision_id:
            print(f"   Retrieved decision: {response['title']}")
            return True
        return False

    def test_delete_decision(self):
        """Test deleting a decision"""
        if not self.guest_id or not self.decision_id:
            print("   ❌ No guest_id or decision_id available for delete test")
            return False
            
        success, response = self.run_test(
            "Delete Decision", 
            "DELETE", 
            f"decisions/{self.decision_id}", 
            200, 
            params={"guest_id": self.guest_id}
        )
        
        if success and response.get('ok'):
            print(f"   Decision deleted successfully")
            return True
        return False

def main():
    print("🚀 Starting Smart Decision AI Backend Tests")
    print("=" * 50)
    
    tester = SmartDecisionAPITester()
    
    # Run all tests in sequence
    tests = [
        ("API Root", tester.test_root_endpoint),
        ("Guest Session", tester.test_guest_session),
        ("Status Endpoints", tester.test_status_endpoints),
        ("AI Follow-ups Generation", tester.test_followups_generation),
        ("AI Decision Analysis", tester.test_decision_analysis),
        ("Save Decision", tester.test_save_decision),
        ("List Decisions", tester.test_list_decisions),
        ("Get Decision", tester.test_get_decision),
        ("Delete Decision", tester.test_delete_decision),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Backend tests mostly successful!")
        return 0
    else:
        print("⚠️  Backend has significant issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())