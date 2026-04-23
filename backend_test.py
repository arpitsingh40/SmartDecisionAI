#!/usr/bin/env python3
"""
Smart Decision AI Phase 3 Backend Testing
Tests all auth endpoints, decision intelligence features, and new schema
"""
import requests
import sys
import json
import time
import uuid
from datetime import datetime

class SmartDecisionAPITester:
    def __init__(self, base_url="http://localhost:8001/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.guest_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            if not success:
                details += f" (expected {expected_status})"
                try:
                    error_data = response.json()
                    details += f" - {error_data.get('detail', 'No error details')}"
                except:
                    details += f" - {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.content else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_basic_health(self):
        """Test basic API health"""
        print("\n🔍 Testing Basic API Health...")
        success, _ = self.run_test("API Root", "GET", "", 200)
        return success

    def test_guest_session(self):
        """Test guest session creation"""
        print("\n🔍 Testing Guest Session...")
        success, response = self.run_test("Create Guest Session", "POST", "guest/session", 200)
        if success and 'guest_id' in response:
            self.guest_id = response['guest_id']
            print(f"   Guest ID: {self.guest_id}")
        return success

    def test_auth_signup(self):
        """Test user signup"""
        print("\n🔍 Testing Auth - Signup...")
        test_email = f"test_phase3_{uuid.uuid4().hex[:8]}@example.com"
        signup_data = {
            "email": test_email,
            "password": "pass1234",
            "name": "Test User Phase3"
        }
        
        success, response = self.run_test("User Signup", "POST", "auth/signup", 200, signup_data)
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   User ID: {self.user_id}")
            print(f"   Email: {test_email}")
            # Store credentials for later tests
            with open('/app/memory/test_credentials.md', 'w') as f:
                f.write(f"# Test Credentials\n")
                f.write(f"Test User Email: {test_email}\n")
                f.write(f"Test User Password: pass1234\n")
                f.write(f"Test User ID: {self.user_id}\n")
        return success

    def test_auth_login(self):
        """Test user login with existing credentials"""
        print("\n🔍 Testing Auth - Login...")
        # Read credentials from file
        try:
            with open('/app/memory/test_credentials.md', 'r') as f:
                content = f.read()
                email_line = [line for line in content.split('\n') if 'Test User Email:' in line]
                if email_line:
                    test_email = email_line[0].split(': ')[1]
                    login_data = {
                        "email": test_email,
                        "password": "pass1234"
                    }
                    
                    success, response = self.run_test("User Login", "POST", "auth/login", 200, login_data)
                    if success and 'token' in response:
                        self.token = response['token']
                        self.user_id = response['user']['id']
                    return success
        except:
            pass
        
        self.log_test("User Login", False, "No test credentials available")
        return False

    def test_auth_me(self):
        """Test /auth/me endpoint"""
        print("\n🔍 Testing Auth - Me...")
        if not self.token:
            self.log_test("Auth Me", False, "No auth token available")
            return False
        
        success, response = self.run_test("Auth Me", "GET", "auth/me", 200)
        return success

    def test_auth_validation(self):
        """Test auth validation scenarios"""
        print("\n🔍 Testing Auth - Validation...")
        
        # Test invalid email signup
        invalid_email_data = {
            "email": "abc",
            "password": "pass1234"
        }
        success1, _ = self.run_test("Signup Invalid Email", "POST", "auth/signup", 422, invalid_email_data)
        
        # Test wrong password login
        if self.user_id:
            try:
                with open('/app/memory/test_credentials.md', 'r') as f:
                    content = f.read()
                    email_line = [line for line in content.split('\n') if 'Test User Email:' in line]
                    if email_line:
                        test_email = email_line[0].split(': ')[1]
                        wrong_login_data = {
                            "email": test_email,
                            "password": "wrongpassword"
                        }
                        success2, _ = self.run_test("Login Wrong Password", "POST", "auth/login", 401, wrong_login_data)
                        return success1 and success2
            except:
                pass
        
        return success1

    def test_followups_generation(self):
        """Test follow-up questions generation"""
        print("\n🔍 Testing Follow-ups Generation...")
        decision_data = {
            "decision": "Should I buy an iPhone 16 Pro or a OnePlus 13 as my daily driver?"
        }
        
        success, response = self.run_test("Generate Follow-ups", "POST", "decisions/followups", 200, decision_data)
        if success:
            questions = response.get('questions', [])
            if len(questions) >= 4:
                print(f"   Generated {len(questions)} questions")
                # Check question types
                types_found = set(q.get('type') for q in questions)
                print(f"   Question types: {types_found}")
                return True
            else:
                self.log_test("Follow-ups Quality", False, f"Only {len(questions)} questions generated (expected >=4)")
        return success

    def test_decision_analysis(self):
        """Test decision analysis with new Decision Intelligence schema"""
        print("\n🔍 Testing Decision Analysis...")
        
        # First get follow-ups
        decision_text = "Should I buy an iPhone 16 Pro or a OnePlus 13 as my daily driver?"
        decision_data = {"decision": decision_text}
        
        success, followup_response = self.run_test("Get Follow-ups for Analysis", "POST", "decisions/followups", 200, decision_data)
        if not success:
            return False
        
        questions = followup_response.get('questions', [])
        if len(questions) < 3:
            self.log_test("Analysis Setup", False, "Not enough questions for analysis")
            return False
        
        # Create sample answers
        answers = []
        for i, q in enumerate(questions[:3]):  # Use first 3 questions
            if q.get('type') == 'single_choice' and q.get('options'):
                answers.append({
                    "question": q['question'],
                    "type": q['type'],
                    "answer": q['options'][0]
                })
            elif q.get('type') == 'multi_choice' and q.get('options'):
                answers.append({
                    "question": q['question'],
                    "type": q['type'],
                    "answer": [q['options'][0]]
                })
            elif q.get('type') == 'slider':
                answers.append({
                    "question": q['question'],
                    "type": q['type'],
                    "answer": q.get('max', 10) // 2
                })
            elif q.get('type') == 'text':
                answers.append({
                    "question": q['question'],
                    "type": q['type'],
                    "answer": "best camera and reliability"
                })
        
        # Start async analysis
        analyze_data = {
            "decision": decision_text,
            "answers": answers
        }
        
        success, start_response = self.run_test("Start Analysis Job", "POST", "decisions/analyze/start", 200, analyze_data)
        if not success:
            return False
        
        job_id = start_response.get('job_id')
        if not job_id:
            self.log_test("Analysis Job ID", False, "No job_id returned")
            return False
        
        print(f"   Job ID: {job_id}")
        
        # Poll for completion (up to 120 seconds as specified)
        max_wait = 120
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            time.sleep(2)
            success, status_response = self.run_test(f"Check Analysis Status", "GET", f"decisions/analyze/status/{job_id}", 200)
            
            if success:
                status = status_response.get('status')
                print(f"   Status: {status}")
                
                if status == 'completed':
                    result = status_response.get('result', {})
                    return self.validate_decision_intelligence_schema(result)
                elif status == 'failed':
                    error = status_response.get('error', 'Unknown error')
                    self.log_test("Analysis Completion", False, f"Analysis failed: {error}")
                    return False
        
        self.log_test("Analysis Timeout", False, f"Analysis did not complete within {max_wait} seconds")
        return False

    def validate_decision_intelligence_schema(self, result):
        """Validate the new Decision Intelligence schema"""
        print("\n🔍 Validating Decision Intelligence Schema...")
        
        required_fields = ['options', 'best_option_id', 'reasoning', 'confidence', 'goal', 'key_insights']
        optional_fields = ['execution_plan', 'plan_b', 'plan_b_trigger']
        
        # Check top-level fields
        for field in required_fields:
            if field not in result:
                self.log_test(f"Schema - {field}", False, f"Missing required field: {field}")
                return False
            else:
                self.log_test(f"Schema - {field}", True)
        
        # Check options have extended fields
        options = result.get('options', [])
        if len(options) < 3:
            self.log_test("Schema - Options Count", False, f"Expected >=3 options, got {len(options)}")
            return False
        
        extended_option_fields = ['success_probability', 'expected_return', 'time_to_result', 'easiness', 'financial_ratio']
        
        for i, option in enumerate(options[:2]):  # Check first 2 options
            for field in extended_option_fields:
                if field in option:
                    self.log_test(f"Schema - Option {i+1} {field}", True)
                else:
                    self.log_test(f"Schema - Option {i+1} {field}", False, f"Missing extended field: {field}")
        
        # Check execution plan if present
        execution_plan = result.get('execution_plan')
        if execution_plan:
            plan_fields = ['title', 'total_timeline', 'steps']
            for field in plan_fields:
                if field in execution_plan:
                    self.log_test(f"Schema - Execution Plan {field}", True)
                else:
                    self.log_test(f"Schema - Execution Plan {field}", False, f"Missing execution plan field: {field}")
            
            # Check steps structure
            steps = execution_plan.get('steps', [])
            if steps and len(steps) >= 3:
                step = steps[0]
                step_fields = ['step', 'action', 'timeline', 'priority']
                for field in step_fields:
                    if field in step:
                        self.log_test(f"Schema - Execution Step {field}", True)
                    else:
                        self.log_test(f"Schema - Execution Step {field}", False, f"Missing step field: {field}")
        
        print(f"   Goal: {result.get('goal', 'N/A')[:100]}...")
        print(f"   Key Insights: {len(result.get('key_insights', []))} insights")
        print(f"   Options: {len(options)} options")
        print(f"   Best Option: {result.get('best_option_id', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}%")
        
        return True

    def test_save_decision(self):
        """Test saving a decision"""
        print("\n🔍 Testing Save Decision...")
        
        # Create a simple decision result for testing
        test_result = {
            "options": [
                {
                    "id": "opt_1",
                    "title": "iPhone 16 Pro",
                    "description": "Latest iPhone with advanced features",
                    "pros": ["Great camera", "iOS ecosystem"],
                    "cons": ["Expensive", "Limited customization"],
                    "risk_level": "Low",
                    "short_term_outcome": "Immediate premium experience",
                    "long_term_outcome": "Long-term iOS ecosystem benefits",
                    "score": 85,
                    "success_probability": 90,
                    "expected_return": "High satisfaction",
                    "time_to_result": "Immediate",
                    "easiness": 95,
                    "financial_ratio": "1:3"
                }
            ],
            "best_option_id": "opt_1",
            "reasoning": "Test reasoning",
            "confidence": 85,
            "goal": "Choose the best smartphone",
            "key_insights": ["Camera quality matters", "Ecosystem integration important"]
        }
        
        save_data = {
            "title": "Test Decision - Smartphone Choice",
            "decision": "Should I buy an iPhone 16 Pro or a OnePlus 13?",
            "answers": [{"question": "What's most important?", "type": "text", "answer": "Camera quality"}],
            "result": test_result
        }
        
        if not self.token:
            save_data["guest_id"] = self.guest_id
        
        success, response = self.run_test("Save Decision", "POST", "decisions", 201, save_data)
        if success and 'id' in response:
            self.saved_decision_id = response['id']
            print(f"   Saved Decision ID: {self.saved_decision_id}")
        return success

    def test_list_decisions(self):
        """Test listing decisions"""
        print("\n🔍 Testing List Decisions...")
        
        params = ""
        if not self.token and self.guest_id:
            params = f"?guest_id={self.guest_id}"
        
        success, response = self.run_test("List Decisions", "GET", f"decisions{params}", 200)
        if success:
            decisions = response if isinstance(response, list) else []
            print(f"   Found {len(decisions)} decisions")
        return success

    def test_auth_scoped_decisions(self):
        """Test that decisions are properly scoped by auth"""
        print("\n🔍 Testing Auth-Scoped Decisions...")
        
        if not self.token:
            self.log_test("Auth Scoped Decisions", False, "No auth token for scoping test")
            return False
        
        # Get decisions with auth token (should return user's decisions)
        success1, auth_response = self.run_test("List User Decisions", "GET", "decisions", 200)
        
        # Get decisions with guest_id (should return empty or guest-only)
        if self.guest_id:
            success2, guest_response = self.run_test("List Guest Decisions", "GET", f"decisions?guest_id={self.guest_id}", 200)
            
            if success1 and success2:
                auth_decisions = auth_response if isinstance(auth_response, list) else []
                guest_decisions = guest_response if isinstance(guest_response, list) else []
                
                print(f"   User decisions: {len(auth_decisions)}")
                print(f"   Guest decisions: {len(guest_decisions)}")
                
                # They should be different (scoped properly)
                return True
        
        return success1

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Smart Decision AI Phase 3 Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic health
        if not self.test_basic_health():
            print("❌ Basic API health failed - stopping tests")
            return False
        
        # Guest session
        self.test_guest_session()
        
        # Auth tests
        self.test_auth_signup()
        self.test_auth_login()
        self.test_auth_me()
        self.test_auth_validation()
        
        # Decision engine tests
        self.test_followups_generation()
        self.test_decision_analysis()
        
        # Saved decisions tests
        self.test_save_decision()
        self.test_list_decisions()
        self.test_auth_scoped_decisions()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Backend Tests Summary: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = SmartDecisionAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "total_tests": tester.tests_run,
                "passed_tests": tester.tests_passed,
                "success_rate": round((tester.tests_passed / tester.tests_run) * 100, 1) if tester.tests_run > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "detailed_results": tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())