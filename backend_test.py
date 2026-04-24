#!/usr/bin/env python3
"""
Smart Decision AI Phase 6 Backend Testing - MULTI-AGENT BOARDROOM
Tests all auth endpoints, decision intelligence features, and Phase 6 multi-agent system:
- Factor suggestion endpoint
- Enhanced analysis with factors and user_level
- Phase 4 schema fields (factor_ratings, scenarios, future_impact, assumptions, bias_flags)
- Phase 5 execution engine fields (key_reasons, expected_outcome, risks, automation_layer, kpis, monetization, scorecard)
- Phase 6 multi-agent fields (debate, agent_perspectives, _engine)
- Action buttons with real tool URLs and automation shortcuts
- Multi-agent async job pattern with 60-180s execution time
"""
import requests
import sys
import json
import time
import uuid
from datetime import datetime

class SmartDecisionAPITester:
    def __init__(self, base_url="https://decide-pro-1.preview.emergentagent.com/api"):
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

    def test_suggest_factors(self):
        """Test Phase 4 factor suggestion endpoint"""
        print("\n🔍 Testing Phase 4 - Factor Suggestion...")
        decision_data = {
            "decision": "Should I buy a used Toyota Camry or a new Honda Civic?"
        }
        
        success, response = self.run_test("Suggest Factors", "POST", "decisions/suggest-factors", 200, decision_data)
        if success:
            factors = response.get('factors', [])
            if len(factors) >= 3:
                print(f"   Generated {len(factors)} factors")
                for i, factor in enumerate(factors[:3]):
                    print(f"   Factor {i+1}: {factor.get('name')} (weight: {factor.get('default_weight')})")
                    if not factor.get('name') or not factor.get('description'):
                        self.log_test("Factor Quality", False, f"Factor {i+1} missing name or description")
                        return False
                self.log_test("Factor Quality", True)
                return True
            else:
                self.log_test("Factor Count", False, f"Only {len(factors)} factors generated (expected >=3)")
        return success

    def test_decision_analysis_with_factors(self):
        """Test decision analysis with Phase 4 factors"""
        print("\n🔍 Testing Phase 4 - Decision Analysis with Factors...")
        
        # First get factors
        decision_text = "Should I buy a used Toyota Camry or a new Honda Civic?"
        decision_data = {"decision": decision_text}
        
        success, factor_response = self.run_test("Get Factors for Analysis", "POST", "decisions/suggest-factors", 200, decision_data)
        if not success:
            return False
        
        factors = factor_response.get('factors', [])
        if len(factors) < 3:
            self.log_test("Analysis Setup", False, "Not enough factors for analysis")
            return False
        
        # Get follow-ups
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
                    "answer": "reliability and cost"
                })
        
        # Prepare factors for analysis
        factor_weights = []
        for i, factor in enumerate(factors[:4]):  # Use first 4 factors
            factor_weights.append({
                "name": factor['name'],
                "weight": factor.get('default_weight', 50)
            })
        
        # Start async analysis with factors
        analyze_data = {
            "decision": decision_text,
            "answers": answers,
            "factors": factor_weights
        }
        
        success, start_response = self.run_test("Start Analysis Job with Factors", "POST", "decisions/analyze/start", 200, analyze_data)
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
            time.sleep(3)
            success, status_response = self.run_test(f"Check Analysis Status", "GET", f"decisions/analyze/status/{job_id}", 200)
            
            if success:
                status = status_response.get('status')
                print(f"   Status: {status}")
                
                if status == 'completed':
                    result = status_response.get('result', {})
                    # First validate basic Phase 4 schema, then Phase 5 additions
                    basic_valid = self.validate_basic_schema(result)
                    phase5_valid = self.validate_phase5_additions(result)
                    return basic_valid and phase5_valid
                elif status == 'failed':
                    error = status_response.get('error', 'Unknown error')
                    self.log_test("Analysis Completion", False, f"Analysis failed: {error}")
                    return False
        
        self.log_test("Analysis Timeout", False, f"Analysis did not complete within {max_wait} seconds")
        return False

    def test_decision_analysis_with_factors_phase5(self):
        """Test decision analysis with Phase 5 execution engine features"""
        print("\n🔍 Testing Phase 5 - Decision Analysis with Execution Engine...")
        
        # Test the specific payload from the review request
        decision_text = "Launch a productized newsletter writing service"
        analyze_data = {
            "decision": decision_text,
            "answers": [],
            "factors": [{"name": "Revenue", "weight": 80}],
            "user_level": "intermediate"
        }
        
        success, start_response = self.run_test("Start Phase 5 Analysis Job", "POST", "decisions/analyze/start", 200, analyze_data)
        if not success:
            return False
        
        job_id = start_response.get('job_id')
        if not job_id:
            self.log_test("Phase 5 Analysis Job ID", False, "No job_id returned")
            return False
        
        print(f"   Job ID: {job_id}")
        
        # Poll for completion (up to 120 seconds as specified)
        max_wait = 120
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            time.sleep(5)  # Longer wait for Phase 5 analysis
            success, status_response = self.run_test(f"Check Phase 5 Analysis Status", "GET", f"decisions/analyze/status/{job_id}", 200)
            
            if success:
                status = status_response.get('status')
                print(f"   Status: {status}")
                
                if status == 'completed':
                    result = status_response.get('result', {})
                    return self.validate_phase5_schema(result)
                elif status == 'failed':
                    error = status_response.get('error', 'Unknown error')
                    self.log_test("Phase 5 Analysis Completion", False, f"Analysis failed: {error}")
                    return False
        
        self.log_test("Phase 5 Analysis Timeout", False, f"Analysis did not complete within {max_wait} seconds")
        return False

    def test_multi_agent_analysis_phase6(self):
        """Test Phase 6 multi-agent analysis with 6 agents + synthesizer"""
        print("\n🔍 Testing Phase 6 - Multi-Agent Boardroom Analysis...")
        
        # Use a decision that will trigger multi-agent analysis
        decision_text = "Should I buy a used Toyota Corolla for $12k or keep using the metro?"
        analyze_data = {
            "decision": decision_text,
            "answers": [
                {"question": "Commute?", "answer": "$140/mo metro"},
                {"question": "Car need?", "answer": "2-3x/week errands"},
                {"question": "Budget?", "answer": "$350/mo"}
            ],
            "factors": [
                {"name": "Total cost", "weight": 70},
                {"name": "Convenience", "weight": 60},
                {"name": "Flexibility", "weight": 50}
            ],
            "user_level": "intermediate"
        }
        
        success, start_response = self.run_test("Start Phase 6 Multi-Agent Analysis", "POST", "decisions/analyze/start", 200, analyze_data)
        if not success:
            return False
        
        job_id = start_response.get('job_id')
        if not job_id:
            self.log_test("Phase 6 Analysis Job ID", False, "No job_id returned")
            return False
        
        print(f"   Job ID: {job_id}")
        print("   ⏳ Multi-agent analysis takes 60-180s (6 agents + synthesizer)...")
        
        # Poll for completion (up to 240 seconds for multi-agent)
        max_wait = 240
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            time.sleep(8)  # Longer wait for multi-agent analysis
            success, status_response = self.run_test(f"Check Multi-Agent Status", "GET", f"decisions/analyze/status/{job_id}", 200)
            
            if success:
                status = status_response.get('status')
                elapsed = int(time.time() - start_time)
                print(f"   Status: {status} (elapsed: {elapsed}s)")
                
                if status == 'completed':
                    result = status_response.get('result', {})
                    return self.validate_phase6_schema(result)
                elif status == 'failed':
                    error = status_response.get('error', 'Unknown error')
                    self.log_test("Phase 6 Analysis Completion", False, f"Multi-agent analysis failed: {error}")
                    return False
        
        self.log_test("Phase 6 Analysis Timeout", False, f"Multi-agent analysis did not complete within {max_wait} seconds")
        return False

    def test_boardroom_payload_seeding(self):
        """Test seeding a pre-made boardroom decision for frontend testing"""
        print("\n🔍 Testing Boardroom Payload Seeding...")
        
        # Load the pre-made boardroom payload
        try:
            with open('/tmp/boardroom_payload.json', 'r') as f:
                payload = json.load(f)
            
            # Add guest_id if not authenticated
            if not self.token and self.guest_id:
                payload["guest_id"] = self.guest_id
            
            success, response = self.run_test("Seed Boardroom Decision", "POST", "decisions", 201, payload)
            if success and 'id' in response:
                self.boardroom_decision_id = response['id']
                print(f"   Seeded Boardroom Decision ID: {self.boardroom_decision_id}")
                
                # Verify the seeded decision has boardroom structure
                params = ""
                if not self.token and self.guest_id:
                    params = f"?guest_id={self.guest_id}"
                
                success2, get_response = self.run_test("Verify Boardroom Decision", "GET", f"decisions/{self.boardroom_decision_id}{params}", 200)
                if success2:
                    result = get_response.get('result', {})
                    has_debate = 'debate' in result
                    has_agents = 'agent_perspectives' in result and len(result.get('agent_perspectives', [])) == 6
                    
                    self.log_test("Boardroom Decision - Debate", has_debate, "Missing debate field" if not has_debate else "")
                    self.log_test("Boardroom Decision - 6 Agents", has_agents, f"Expected 6 agents, got {len(result.get('agent_perspectives', []))}" if not has_agents else "")
                    
                    return success2
            return success
            
        except Exception as e:
            self.log_test("Boardroom Payload Seeding", False, f"Error loading payload: {str(e)}")
            return False

    def validate_basic_schema(self, result):
        """Validate basic decision schema"""
        required_fields = ['options', 'best_option_id', 'reasoning', 'confidence', 'goal', 'key_insights']
        
        for field in required_fields:
            if field not in result:
                self.log_test(f"Basic Schema - {field}", False, f"Missing required field: {field}")
                return False
            else:
                self.log_test(f"Basic Schema - {field}", True)
        return True

    def validate_phase5_additions(self, result):
        """Validate Phase 5 specific additions"""
        phase5_fields = {
            'key_reasons': list,
            'expected_outcome': dict,
            'risks': list,
            'automation_layer': list,
            'kpis': list,
            'monetization': dict,
            'scorecard': dict
        }
        
        all_valid = True
        for field, expected_type in phase5_fields.items():
            if field in result:
                value = result[field]
                if isinstance(value, expected_type):
                    self.log_test(f"Phase5 Schema - {field}", True)
                else:
                    self.log_test(f"Phase5 Schema - {field}", False, f"Wrong type: expected {expected_type.__name__}, got {type(value).__name__}")
                    all_valid = False
            else:
                self.log_test(f"Phase5 Schema - {field}", False, f"Missing Phase 5 field: {field}")
                all_valid = False
        
        return all_valid
        """Validate the Phase 5 Execution Engine schema"""
        print("\n🔍 Validating Phase 4 Decision Intelligence Schema...")
        
        required_fields = ['options', 'best_option_id', 'reasoning', 'confidence', 'goal', 'key_insights']
        phase4_fields = ['assumptions', 'bias_flags', 'factors_used']
        
        # Check top-level fields
        for field in required_fields:
            if field not in result:
                self.log_test(f"Schema - {field}", False, f"Missing required field: {field}")
                return False
            else:
                self.log_test(f"Schema - {field}", True)
        
        # Check Phase 4 fields
        for field in phase4_fields:
            if field in result:
                self.log_test(f"Phase4 Schema - {field}", True)
            else:
                self.log_test(f"Phase4 Schema - {field}", False, f"Missing Phase 4 field: {field}")
        
        # Check options have Phase 4 extended fields
        options = result.get('options', [])
        if len(options) < 3:
            self.log_test("Schema - Options Count", False, f"Expected >=3 options, got {len(options)}")
            return False
        
        # Check for "Do nothing" option
        do_nothing_found = any(opt.get('is_do_nothing') for opt in options)
        self.log_test("Phase4 Schema - Do Nothing Option", do_nothing_found, "No 'do nothing' option found" if not do_nothing_found else "")
        
        phase4_option_fields = ['factor_ratings', 'scenarios', 'future_impact']
        
        for i, option in enumerate(options[:2]):  # Check first 2 options
            # Check factor_ratings
            factor_ratings = option.get('factor_ratings', {})
            if factor_ratings:
                self.log_test(f"Phase4 Schema - Option {i+1} factor_ratings", True)
                # Check if ratings exist for provided factors
                factor_names = [f['name'] for f in factors]
                for factor_name in factor_names:
                    if factor_name in factor_ratings:
                        rating = factor_ratings[factor_name]
                        if isinstance(rating, (int, float)) and 0 <= rating <= 10:
                            self.log_test(f"Phase4 Schema - Option {i+1} {factor_name} rating", True)
                        else:
                            self.log_test(f"Phase4 Schema - Option {i+1} {factor_name} rating", False, f"Invalid rating: {rating}")
            else:
                self.log_test(f"Phase4 Schema - Option {i+1} factor_ratings", False, "Missing factor_ratings")
            
            # Check scenarios
            scenarios = option.get('scenarios', {})
            if scenarios:
                scenario_fields = ['best_case', 'worst_case', 'most_likely']
                for field in scenario_fields:
                    if field in scenarios:
                        self.log_test(f"Phase4 Schema - Option {i+1} scenario {field}", True)
                    else:
                        self.log_test(f"Phase4 Schema - Option {i+1} scenario {field}", False, f"Missing scenario field: {field}")
            else:
                self.log_test(f"Phase4 Schema - Option {i+1} scenarios", False, "Missing scenarios")
            
            # Check future_impact
            future_impact = option.get('future_impact', {})
            if future_impact:
                future_fields = ['one_year', 'five_year']
                for field in future_fields:
                    if field in future_impact:
                        self.log_test(f"Phase4 Schema - Option {i+1} future {field}", True)
                    else:
                        self.log_test(f"Phase4 Schema - Option {i+1} future {field}", False, f"Missing future field: {field}")
            else:
                self.log_test(f"Phase4 Schema - Option {i+1} future_impact", False, "Missing future_impact")
        
        # Check execution plan if present
        execution_plan = result.get('execution_plan')
        if execution_plan:
            plan_fields = ['title', 'total_timeline', 'steps']
            for field in plan_fields:
                if field in execution_plan:
                    self.log_test(f"Schema - Execution Plan {field}", True)
                else:
                    self.log_test(f"Schema - Execution Plan {field}", False, f"Missing execution plan field: {field}")
        
        # Check assumptions
        assumptions = result.get('assumptions', [])
        if assumptions:
            print(f"   Assumptions: {len(assumptions)} found")
        
        # Check bias_flags
        bias_flags = result.get('bias_flags', [])
        if bias_flags:
            print(f"   Bias Flags: {len(bias_flags)} found")
            for flag in bias_flags:
                if 'title' in flag and 'message' in flag and 'severity' in flag:
                    self.log_test(f"Phase4 Schema - Bias Flag Structure", True)
                else:
                    self.log_test(f"Phase4 Schema - Bias Flag Structure", False, "Invalid bias flag structure")
        
        print(f"   Goal: {result.get('goal', 'N/A')[:100]}...")
        print(f"   Key Insights: {len(result.get('key_insights', []))} insights")
        print(f"   Options: {len(options)} options")
        print(f"   Best Option: {result.get('best_option_id', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}%")
        print(f"   Factors Used: {result.get('factors_used', [])}")
        
        return True
        """Validate the Phase 5 Execution Engine schema"""
        print("\n🔍 Validating Phase 5 Execution Engine Schema...")
        
        # Phase 5 new fields
        phase5_fields = {
            'key_reasons': list,
            'expected_outcome': dict,
            'risks': list,
            'automation_layer': list,
            'kpis': list,
            'monetization': dict,
            'scorecard': dict
        }
        
        # Check Phase 5 fields
        for field, expected_type in phase5_fields.items():
            if field in result:
                value = result[field]
                if isinstance(value, expected_type):
                    self.log_test(f"Phase5 Schema - {field}", True)
                    
                    # Detailed validation for each field
                    if field == 'key_reasons':
                        if len(value) >= 3:
                            self.log_test(f"Phase5 Schema - {field} count", True, f"Found {len(value)} key reasons")
                        else:
                            self.log_test(f"Phase5 Schema - {field} count", False, f"Expected >=3 key reasons, got {len(value)}")
                    
                    elif field == 'expected_outcome':
                        outcome_fields = ['revenue_increase', 'cost_savings', 'time_saved', 'non_financial']
                        for outcome_field in outcome_fields:
                            if outcome_field in value:
                                self.log_test(f"Phase5 Schema - expected_outcome.{outcome_field}", True)
                                
                                # Check money range structure
                                if outcome_field in ['revenue_increase', 'cost_savings'] and isinstance(value[outcome_field], dict):
                                    money_range = value[outcome_field]
                                    range_fields = ['realistic_low', 'realistic_high', 'best_case']
                                    for range_field in range_fields:
                                        if range_field in money_range:
                                            self.log_test(f"Phase5 Schema - {outcome_field}.{range_field}", True)
                    
                    elif field == 'risks':
                        if len(value) > 0:
                            risk_fields = ['risk', 'severity', 'probability', 'mitigation']
                            for i, risk_item in enumerate(value[:2]):  # Check first 2 risks
                                for risk_field in risk_fields:
                                    if risk_field in risk_item:
                                        self.log_test(f"Phase5 Schema - risks[{i}].{risk_field}", True)
                                    else:
                                        self.log_test(f"Phase5 Schema - risks[{i}].{risk_field}", False, f"Missing risk field: {risk_field}")
                    
                    elif field == 'automation_layer':
                        if len(value) > 0:
                            auto_fields = ['area', 'tools', 'how_it_helps', 'plug_and_play']
                            for i, auto_item in enumerate(value[:2]):  # Check first 2 automation ideas
                                for auto_field in auto_fields:
                                    if auto_field in auto_item:
                                        self.log_test(f"Phase5 Schema - automation_layer[{i}].{auto_field}", True)
                    
                    elif field == 'kpis':
                        if len(value) > 0:
                            kpi_fields = ['name', 'how_to_measure', 'target', 'leading_indicator']
                            for i, kpi_item in enumerate(value[:2]):  # Check first 2 KPIs
                                for kpi_field in kpi_fields:
                                    if kpi_field in kpi_item:
                                        self.log_test(f"Phase5 Schema - kpis[{i}].{kpi_field}", True)
                    
                    elif field == 'monetization':
                        monetization_fields = ['services', 'products', 'upsells']
                        for mon_field in monetization_fields:
                            if mon_field in value:
                                self.log_test(f"Phase5 Schema - monetization.{mon_field}", True)
                    
                    elif field == 'scorecard':
                        scorecard_fields = ['score', 'risk_level', 'time_to_result', 'ease_of_execution', 'confidence']
                        for score_field in scorecard_fields:
                            if score_field in value:
                                self.log_test(f"Phase5 Schema - scorecard.{score_field}", True)
                            else:
                                self.log_test(f"Phase5 Schema - scorecard.{score_field}", False, f"Missing scorecard field: {score_field}")
                
                else:
                    self.log_test(f"Phase5 Schema - {field}", False, f"Wrong type: expected {expected_type.__name__}, got {type(value).__name__}")
            else:
                self.log_test(f"Phase5 Schema - {field}", False, f"Missing Phase 5 field: {field}")
        
        # Check execution plan has Phase 5 enhancements
        execution_plan = result.get('execution_plan')
        if execution_plan and 'steps' in execution_plan:
            steps = execution_plan['steps']
            if len(steps) > 0:
                step = steps[0]
                phase5_step_fields = ['days', 'difficulty', 'action_button']
                for step_field in phase5_step_fields:
                    if step_field in step:
                        self.log_test(f"Phase5 Schema - execution_plan.steps[0].{step_field}", True)
                        
                        # Check action button structure
                        if step_field == 'action_button' and isinstance(step[step_field], dict):
                            action_button = step[step_field]
                            button_fields = ['label', 'tool', 'url', 'instruction', 'automation_shortcut']
                            for button_field in button_fields:
                                if button_field in action_button:
                                    self.log_test(f"Phase5 Schema - action_button.{button_field}", True)
                    else:
                        self.log_test(f"Phase5 Schema - execution_plan.steps[0].{step_field}", False, f"Missing step field: {step_field}")
        
        # Print summary of Phase 5 fields
        print(f"   Key Reasons: {len(result.get('key_reasons', []))} items")
        print(f"   Expected Outcome: {bool(result.get('expected_outcome'))}")
        print(f"   Risks: {len(result.get('risks', []))} items")
        print(f"   Automation Layer: {len(result.get('automation_layer', []))} items")
        print(f"   KPIs: {len(result.get('kpis', []))} items")
        print(f"   Monetization: {bool(result.get('monetization'))}")
        print(f"   Scorecard: {bool(result.get('scorecard'))}")
        
        if result.get('scorecard'):
            scorecard = result['scorecard']
            print(f"   Scorecard Score: {scorecard.get('score', 'N/A')}")
            print(f"   Scorecard Risk: {scorecard.get('risk_level', 'N/A')}")
            print(f"   Scorecard Time: {scorecard.get('time_to_result', 'N/A')}")
            print(f"   Scorecard Ease: {scorecard.get('ease_of_execution', 'N/A')}")
            print(f"   Scorecard Confidence: {scorecard.get('confidence', 'N/A')}")
        
        return True

    def validate_phase6_schema(self, result):
        """Validate the Phase 6 Multi-Agent Boardroom schema"""
        print("\n🔍 Validating Phase 6 Multi-Agent Boardroom Schema...")
        
        # First validate Phase 5 schema
        phase5_valid = self.validate_phase5_schema(result)
        
        # Phase 6 specific fields
        phase6_fields = {
            'debate': dict,
            'agent_perspectives': list,
            '_engine': str
        }
        
        phase6_valid = True
        
        # Check Phase 6 fields
        for field, expected_type in phase6_fields.items():
            if field in result:
                value = result[field]
                if isinstance(value, expected_type):
                    self.log_test(f"Phase6 Schema - {field}", True)
                    
                    # Detailed validation for each field
                    if field == 'agent_perspectives':
                        expected_agents = ['Strategic', 'Financial', 'Risk', 'Execution', 'Contrarian', 'Optimization']
                        if len(value) == 6:
                            self.log_test(f"Phase6 Schema - agent_perspectives count", True, f"Found {len(value)} agents")
                            
                            # Check each agent
                            found_agents = []
                            for agent in value:
                                agent_name = agent.get('agent', '')
                                found_agents.append(agent_name)
                                
                                # Check agent structure
                                agent_fields = ['agent', 'summary', 'details']
                                for agent_field in agent_fields:
                                    if agent_field in agent:
                                        self.log_test(f"Phase6 Schema - agent.{agent_field}", True)
                                    else:
                                        self.log_test(f"Phase6 Schema - agent.{agent_field}", False, f"Missing agent field: {agent_field}")
                                        phase6_valid = False
                            
                            # Check all expected agents are present
                            for expected_agent in expected_agents:
                                if expected_agent in found_agents:
                                    self.log_test(f"Phase6 Schema - {expected_agent} agent", True)
                                else:
                                    self.log_test(f"Phase6 Schema - {expected_agent} agent", False, f"Missing {expected_agent} agent")
                                    phase6_valid = False
                        else:
                            self.log_test(f"Phase6 Schema - agent_perspectives count", False, f"Expected 6 agents, got {len(value)}")
                            phase6_valid = False
                    
                    elif field == 'debate':
                        debate_fields = ['conflicts', 'trade_offs', 'convergence']
                        for debate_field in debate_fields:
                            if debate_field in value:
                                self.log_test(f"Phase6 Schema - debate.{debate_field}", True)
                                
                                # Check conflicts structure
                                if debate_field == 'conflicts' and isinstance(value[debate_field], list):
                                    conflicts = value[debate_field]
                                    if len(conflicts) > 0:
                                        conflict = conflicts[0]
                                        conflict_fields = ['topic', 'views', 'resolution']
                                        for conflict_field in conflict_fields:
                                            if conflict_field in conflict:
                                                self.log_test(f"Phase6 Schema - conflict.{conflict_field}", True)
                                                
                                                # Check views structure
                                                if conflict_field == 'views' and isinstance(conflict[conflict_field], list):
                                                    views = conflict[conflict_field]
                                                    if len(views) > 0:
                                                        view = views[0]
                                                        view_fields = ['agent', 'view']
                                                        for view_field in view_fields:
                                                            if view_field in view:
                                                                self.log_test(f"Phase6 Schema - view.{view_field}", True)
                                                            else:
                                                                self.log_test(f"Phase6 Schema - view.{view_field}", False, f"Missing view field: {view_field}")
                                            else:
                                                self.log_test(f"Phase6 Schema - conflict.{conflict_field}", False, f"Missing conflict field: {conflict_field}")
                            else:
                                self.log_test(f"Phase6 Schema - debate.{debate_field}", False, f"Missing debate field: {debate_field}")
                    
                    elif field == '_engine':
                        if value in ['multi_agent', 'legacy_fallback']:
                            self.log_test(f"Phase6 Schema - _engine value", True, f"Engine: {value}")
                        else:
                            self.log_test(f"Phase6 Schema - _engine value", False, f"Invalid engine value: {value}")
                            phase6_valid = False
                
                else:
                    self.log_test(f"Phase6 Schema - {field}", False, f"Wrong type: expected {expected_type.__name__}, got {type(value).__name__}")
                    phase6_valid = False
            else:
                self.log_test(f"Phase6 Schema - {field}", False, f"Missing Phase 6 field: {field}")
                phase6_valid = False
        
        # Print summary of Phase 6 fields
        print(f"   Engine Used: {result.get('_engine', 'N/A')}")
        print(f"   Agent Perspectives: {len(result.get('agent_perspectives', []))} agents")
        print(f"   Debate Present: {bool(result.get('debate'))}")
        
        if result.get('debate'):
            debate = result['debate']
            print(f"   Debate Conflicts: {len(debate.get('conflicts', []))}")
            print(f"   Debate Trade-offs: {len(debate.get('trade_offs', []))}")
            print(f"   Debate Convergence: {bool(debate.get('convergence'))}")
        
        if result.get('agent_perspectives'):
            agents = result['agent_perspectives']
            agent_names = [a.get('agent', 'Unknown') for a in agents]
            print(f"   Agents Found: {', '.join(agent_names)}")
        
        return phase5_valid and phase6_valid
        """Validate the Phase 4 Decision Intelligence schema"""
        print("\n🔍 Validating Phase 4 Decision Intelligence Schema...")
        
        required_fields = ['options', 'best_option_id', 'reasoning', 'confidence', 'goal', 'key_insights']
        phase4_fields = ['assumptions', 'bias_flags', 'factors_used']
        
        # Check top-level fields
        for field in required_fields:
            if field not in result:
                self.log_test(f"Schema - {field}", False, f"Missing required field: {field}")
                return False
            else:
                self.log_test(f"Schema - {field}", True)
        
        # Check Phase 4 fields
        for field in phase4_fields:
            if field in result:
                self.log_test(f"Phase4 Schema - {field}", True)
            else:
                self.log_test(f"Phase4 Schema - {field}", False, f"Missing Phase 4 field: {field}")
        
        # Check options have Phase 4 extended fields
        options = result.get('options', [])
        if len(options) < 3:
            self.log_test("Schema - Options Count", False, f"Expected >=3 options, got {len(options)}")
            return False
        
        # Check for "Do nothing" option
        do_nothing_found = any(opt.get('is_do_nothing') for opt in options)
        self.log_test("Phase4 Schema - Do Nothing Option", do_nothing_found, "No 'do nothing' option found" if not do_nothing_found else "")
        
        phase4_option_fields = ['factor_ratings', 'scenarios', 'future_impact']
        
        for i, option in enumerate(options[:2]):  # Check first 2 options
            # Check factor_ratings
            factor_ratings = option.get('factor_ratings', {})
            if factor_ratings:
                self.log_test(f"Phase4 Schema - Option {i+1} factor_ratings", True)
                # Check if ratings exist for provided factors
                factor_names = [f['name'] for f in factors]
                for factor_name in factor_names:
                    if factor_name in factor_ratings:
                        rating = factor_ratings[factor_name]
                        if isinstance(rating, (int, float)) and 0 <= rating <= 10:
                            self.log_test(f"Phase4 Schema - Option {i+1} {factor_name} rating", True)
                        else:
                            self.log_test(f"Phase4 Schema - Option {i+1} {factor_name} rating", False, f"Invalid rating: {rating}")
            else:
                self.log_test(f"Phase4 Schema - Option {i+1} factor_ratings", False, "Missing factor_ratings")
            
            # Check scenarios
            scenarios = option.get('scenarios', {})
            if scenarios:
                scenario_fields = ['best_case', 'worst_case', 'most_likely']
                for field in scenario_fields:
                    if field in scenarios:
                        self.log_test(f"Phase4 Schema - Option {i+1} scenario {field}", True)
                    else:
                        self.log_test(f"Phase4 Schema - Option {i+1} scenario {field}", False, f"Missing scenario field: {field}")
            else:
                self.log_test(f"Phase4 Schema - Option {i+1} scenarios", False, "Missing scenarios")
            
            # Check future_impact
            future_impact = option.get('future_impact', {})
            if future_impact:
                future_fields = ['one_year', 'five_year']
                for field in future_fields:
                    if field in future_impact:
                        self.log_test(f"Phase4 Schema - Option {i+1} future {field}", True)
                    else:
                        self.log_test(f"Phase4 Schema - Option {i+1} future {field}", False, f"Missing future field: {field}")
            else:
                self.log_test(f"Phase4 Schema - Option {i+1} future_impact", False, "Missing future_impact")
        
        # Check execution plan if present
        execution_plan = result.get('execution_plan')
        if execution_plan:
            plan_fields = ['title', 'total_timeline', 'steps']
            for field in plan_fields:
                if field in execution_plan:
                    self.log_test(f"Schema - Execution Plan {field}", True)
                else:
                    self.log_test(f"Schema - Execution Plan {field}", False, f"Missing execution plan field: {field}")
        
        # Check assumptions
        assumptions = result.get('assumptions', [])
        if assumptions:
            print(f"   Assumptions: {len(assumptions)} found")
        
        # Check bias_flags
        bias_flags = result.get('bias_flags', [])
        if bias_flags:
            print(f"   Bias Flags: {len(bias_flags)} found")
            for flag in bias_flags:
                if 'title' in flag and 'message' in flag and 'severity' in flag:
                    self.log_test(f"Phase4 Schema - Bias Flag Structure", True)
                else:
                    self.log_test(f"Phase4 Schema - Bias Flag Structure", False, "Invalid bias flag structure")
        
        print(f"   Goal: {result.get('goal', 'N/A')[:100]}...")
        print(f"   Key Insights: {len(result.get('key_insights', []))} insights")
        print(f"   Options: {len(options)} options")
        print(f"   Best Option: {result.get('best_option_id', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}%")
        print(f"   Factors Used: {result.get('factors_used', [])}")
        
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
        print("🚀 Starting Smart Decision AI Phase 5 Backend Tests")
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
        
        # Phase 4 specific tests
        self.test_suggest_factors()
        self.test_decision_analysis_with_factors()
        
        # Phase 5 specific tests
        self.test_decision_analysis_with_factors_phase5()
        
        # Phase 6 specific tests
        self.test_multi_agent_analysis_phase6()
        self.test_boardroom_payload_seeding()
        
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