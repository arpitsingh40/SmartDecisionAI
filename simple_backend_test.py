#!/usr/bin/env python3
"""
Simple Backend API Test for Smart Decision AI - Quick verification
"""
import requests
import sys
import time
import json

def test_basic_endpoints():
    base_url = "https://decide-pro-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("Testing basic backend endpoints...")
    
    # Test API root
    try:
        response = requests.get(f"{api_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ API Root endpoint working")
        else:
            print(f"❌ API Root failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Root error: {e}")
        return False
    
    # Test guest session
    try:
        response = requests.post(f"{api_url}/guest/session", timeout=10)
        if response.status_code == 200:
            data = response.json()
            guest_id = data.get('guest_id')
            print(f"✅ Guest session created: {guest_id}")
        else:
            print(f"❌ Guest session failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Guest session error: {e}")
        return False
    
    # Test followups with simple decision
    try:
        payload = {"decision": "Should I buy a PS5 or Xbox?"}
        response = requests.post(f"{api_url}/decisions/followups", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            questions = data.get('questions', [])
            print(f"✅ Follow-ups generated: {len(questions)} questions")
        else:
            print(f"❌ Follow-ups failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Follow-ups error: {e}")
        return False
    
    # Test async job start
    try:
        payload = {
            "decision": "Should I buy a PS5 or Xbox?",
            "answers": [
                {"question": "Budget?", "type": "text", "answer": "500"},
                {"question": "Gaming preference?", "type": "single_choice", "answer": "Action games"}
            ]
        }
        response = requests.post(f"{api_url}/decisions/analyze/start", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"✅ Async job started: {job_id}")
            
            # Quick status check
            time.sleep(2)
            status_response = requests.get(f"{api_url}/decisions/analyze/status/{job_id}", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Job status check: {status_data.get('status')}")
            else:
                print(f"⚠️ Job status check failed: {status_response.status_code}")
        else:
            print(f"❌ Async job start failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Async job error: {e}")
        return False
    
    print("✅ Basic backend endpoints are functional")
    return True

if __name__ == "__main__":
    if test_basic_endpoints():
        print("Backend is ready for frontend testing")
        sys.exit(0)
    else:
        print("Backend has issues")
        sys.exit(1)