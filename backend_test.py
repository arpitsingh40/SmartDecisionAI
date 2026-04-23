#!/usr/bin/env python3
"""
Backend API Testing for Smart Decision AI - Iteration 3
Testing the new ASYNC JOB PATTERN for AI analysis
"""
import requests
import sys
import time
import json
from datetime import datetime

class SmartDecisionAPITester:
    def __init__(self, base_url="https://decide-pro-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.guest_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.session.timeout = 30

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    self.log(f"   Error: {error_detail}")
                except:
                    self.log(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_guest_session(self):
        """Test guest session creation"""
        success, response = self.run_test("Guest Session", "POST", "guest/session", 200)
        if success and 'guest_id' in response:
            self.guest_id = response['guest_id']
            self.log(f"   Guest ID: {self.guest_id}")
            return True
        return False

    def test_followups(self):
        """Test follow-up questions generation"""
        decision = "Should I take a PM role at Amazon or stay at Stripe as senior engineer?"
        success, response = self.run_test(
            "Follow-up Questions", 
            "POST", 
            "decisions/followups", 
            200,
            {"decision": decision}
        )
        if success and 'questions' in response:
            questions = response['questions']
            self.log(f"   Generated {len(questions)} questions")
            for i, q in enumerate(questions[:3]):  # Show first 3
                self.log(f"   Q{i+1}: {q.get('question', '')[:60]}... ({q.get('type', 'unknown')})")
            return True, questions
        return False, []

    def test_async_analyze_start(self, decision, answers):
        """Test starting async analysis job"""
        payload = {
            "decision": decision,
            "answers": answers
        }
        success, response = self.run_test(
            "Async Analysis Start", 
            "POST", 
            "decisions/analyze/start", 
            200,
            payload
        )
        if success and 'job_id' in response:
            job_id = response['job_id']
            status = response.get('status', 'unknown')
            self.log(f"   Job ID: {job_id}, Status: {status}")
            return True, job_id
        return False, None

    def test_async_analyze_status(self, job_id, max_wait_seconds=120):
        """Test polling async analysis job status"""
        self.log(f"🔄 Polling job {job_id} status (max {max_wait_seconds}s)...")
        start_time = time.time()
        poll_count = 0
        
        while time.time() - start_time < max_wait_seconds:
            poll_count += 1
            success, response = self.run_test(
                f"Job Status Poll #{poll_count}", 
                "GET", 
                f"decisions/analyze/status/{job_id}", 
                200,
                timeout=10
            )
            
            if not success:
                return False, None
                
            status = response.get('status', 'unknown')
            elapsed = int(time.time() - start_time)
            self.log(f"   Poll #{poll_count} ({elapsed}s): Status = {status}")
            
            if status == 'completed':
                result = response.get('result')
                if result and 'options' in result:
                    options = result['options']
                    best_id = result.get('best_option_id')
                    confidence = result.get('confidence', 0)
                    self.log(f"   ✅ Analysis completed! {len(options)} options, confidence: {confidence}%")
                    self.log(f"   Best option ID: {best_id}")
                    return True, result
                else:
                    self.log(f"   ❌ Completed but missing result data")
                    return False, None
                    
            elif status == 'failed':
                error = response.get('error', 'Unknown error')
                self.log(f"   ❌ Analysis failed: {error}")
                return False, None
                
            elif status == 'pending':
                # Continue polling
                time.sleep(1.5)  # Match frontend polling interval
                continue
            else:
                self.log(f"   ❌ Unknown status: {status}")
                return False, None
                
        self.log(f"   ❌ Timeout after {max_wait_seconds}s")
        return False, None

    def test_save_decision(self, decision, answers, result):
        """Test saving a decision"""
        if not self.guest_id:
            self.log("❌ No guest_id available for save test")
            return False, None
            
        payload = {
            "guest_id": self.guest_id,
            "title": decision[:60],
            "decision": decision,
            "answers": answers,
            "result": result
        }
        success, response = self.run_test(
            "Save Decision", 
            "POST", 
            "decisions", 
            200,
            payload
        )
        if success and 'id' in response:
            decision_id = response['id']
            self.log(f"   Saved decision ID: {decision_id}")
            return True, decision_id
        return False, None

    def test_list_decisions(self):
        """Test listing saved decisions"""
        if not self.guest_id:
            return False, []
            
        success, response = self.run_test(
            "List Decisions", 
            "GET", 
            f"decisions?guest_id={self.guest_id}", 
            200
        )
        if success and isinstance(response, list):
            self.log(f"   Found {len(response)} saved decisions")
            return True, response
        return False, []

    def test_get_decision(self, decision_id):
        """Test retrieving a specific decision"""
        if not self.guest_id or not decision_id:
            return False, None
            
        success, response = self.run_test(
            "Get Decision", 
            "GET", 
            f"decisions/{decision_id}?guest_id={self.guest_id}", 
            200
        )
        if success and 'id' in response:
            self.log(f"   Retrieved decision: {response.get('title', 'Untitled')}")
            return True, response
        return False, None

    def test_delete_decision(self, decision_id):
        """Test deleting a decision"""
        if not self.guest_id or not decision_id:
            return False
            
        success, response = self.run_test(
            "Delete Decision", 
            "DELETE", 
            f"decisions/{decision_id}?guest_id={self.guest_id}", 
            200
        )
        return success

def main():
    print("=" * 60)
    print("Smart Decision AI - Backend API Testing (Iteration 3)")
    print("Testing new ASYNC JOB PATTERN for AI analysis")
    print("=" * 60)
    
    tester = SmartDecisionAPITester()
    
    # Basic API tests
    if not tester.test_root_endpoint()[0]:
        print("❌ API root endpoint failed, stopping tests")
        return 1
        
    if not tester.test_guest_session():
        print("❌ Guest session creation failed, stopping tests")
        return 1
    
    # Test follow-up generation
    success, questions = tester.test_followups()
    if not success:
        print("❌ Follow-up generation failed, stopping tests")
        return 1
    
    # Prepare sample answers for analysis
    sample_answers = [
        {"question": "What's your current role level?", "type": "single_choice", "answer": "Senior Engineer"},
        {"question": "How important is compensation?", "type": "slider", "answer": 8},
        {"question": "What matters most to you?", "type": "multi_choice", "answer": ["Career growth", "Work-life balance"]},
        {"question": "Any specific concerns?", "type": "text", "answer": "Worried about Amazon's work culture"},
        {"question": "Timeline for decision?", "type": "single_choice", "answer": "Within 2 weeks"}
    ]
    
    decision = "Should I take a PM role at Amazon or stay at Stripe as senior engineer?"
    
    # Test the new async analysis pattern
    print("\n" + "=" * 40)
    print("TESTING ASYNC ANALYSIS PATTERN")
    print("=" * 40)
    
    # Start async job
    success, job_id = tester.test_async_analyze_start(decision, sample_answers)
    if not success:
        print("❌ Failed to start async analysis job")
        return 1
    
    # Poll for completion
    success, result = tester.test_async_analyze_status(job_id, max_wait_seconds=120)
    if not success:
        print("❌ Async analysis job failed or timed out")
        return 1
    
    # Test CRUD operations with the result
    print("\n" + "=" * 40)
    print("TESTING CRUD OPERATIONS")
    print("=" * 40)
    
    # Save the decision
    success, decision_id = tester.test_save_decision(decision, sample_answers, result)
    if not success:
        print("❌ Failed to save decision")
        return 1
    
    # List decisions
    success, decisions_list = tester.test_list_decisions()
    if not success:
        print("❌ Failed to list decisions")
        return 1
    
    # Get specific decision
    success, retrieved = tester.test_get_decision(decision_id)
    if not success:
        print("❌ Failed to retrieve decision")
        return 1
    
    # Delete decision
    if not tester.test_delete_decision(decision_id):
        print("❌ Failed to delete decision")
        return 1
    
    # Final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL TESTS PASSED! Async job pattern is working correctly.")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())