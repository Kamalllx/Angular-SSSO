#!/usr/bin/env python3
"""
Comprehensive test script for Smart Study Orchestrator backend
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, timeout=10)
        
        print(f"{method.upper()} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            try:
                result = response.json()
                print(f"✅ Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"✅ Response: {response.text[:200]}...")
            success = True
        else:
            print(f"❌ Expected {expected_status}, got {response.status_code}")
            print(f"Error: {response.text}")
            success = False
        
        print("-" * 50)
        return success
        
    except requests.exceptions.Timeout:
        print(f"❌ {method.upper()} {endpoint} - Request timeout")
        print("-" * 50)
        return False
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {e}")
        print("-" * 50)
        return False

def run_comprehensive_tests():
    """Run comprehensive backend tests"""
    
    print("Smart Study Orchestrator - Comprehensive Backend Test")
    print("=" * 60)
    
    # Basic connectivity tests
    basic_tests = [
        ("GET", "/", 200),
        ("GET", "/health", 200),
        ("GET", "/api/status", 200),
        ("GET", "/api/test-all", 200),
        ("GET", "/api/study/test", 200),
        ("GET", "/api/calendar/test", 200),
    ]
    
    # Study functionality tests
    study_tests = [
        ("GET", "/api/study/sessions", 200),
        ("POST", "/api/study/session", {
            "subject": "Test Mathematics",
            "duration": 25,
            "goals": ["Complete algebra problems", "Review calculus"]
        }, 201),
        ("GET", "/api/study/analytics", 200),
        ("POST", "/api/study/plan", {
            "subject": "Computer Science",
            "duration": 45,
            "goals": ["Learn algorithms", "Practice coding"]
        }, 200),
        ("POST", "/api/study/block-websites", {
            "websites": ["facebook.com", "youtube.com"],
            "duration": 25
        }, 200),
        ("GET", "/api/study/preferences", 200),
    ]
    
    # Calendar functionality tests  
    calendar_tests = [
        ("GET", "/api/calendar/events", 200),
        ("POST", "/api/calendar/event", {
            "title": "Test Study Session",
            "start_time": "2025-05-24T15:00:00",
            "duration": 30,
            "description": "Test event"
        }, 201),
        ("POST", "/api/calendar/schedule-break", {
            "study_duration": 25,
            "break_duration": 5,
            "start_time": "2025-05-24T16:00:00"
        }, 200),
    ]
    
    all_tests = [
        ("Basic Connectivity", basic_tests),
        ("Study Functionality", study_tests),
        ("Calendar Functionality", calendar_tests)
    ]
    
    total_passed = 0
    total_tests = 0
    
    for category, tests in all_tests:
        print(f"\n🔍 Testing {category}")
        print("=" * 40)
        
        category_passed = 0
        for method, endpoint, *args in tests:
            expected_status = args[1] if len(args) > 1 else 200
            data = args[0] if len(args) > 0 and isinstance(args[0], dict) else None
            
            if test_endpoint(method, endpoint, data, expected_status):
                category_passed += 1
            total_tests += 1
            time.sleep(0.3)  # Small delay between tests
        
        total_passed += category_passed
        print(f"{category}: {category_passed}/{len(tests)} passed")
    
    # Test session workflow
    print(f"\n🔍 Testing Session Workflow")
    print("=" * 40)
    
    session_id = None
    
    # Create session
    create_response = requests.post(f"{BASE_URL}/api/study/session", json={
        "subject": "Workflow Test",
        "duration": 30,
        "goals": ["Test session workflow"]
    })
    
    if create_response.status_code == 201:
        session_data = create_response.json()
        session_id = session_data.get('id')
        print(f"✅ Session created: {session_id}")
        total_passed += 1
    else:
        print(f"❌ Failed to create session")
    
    total_tests += 1
    
    # Start session
    if session_id:
        start_response = requests.post(f"{BASE_URL}/api/study/session/{session_id}/start")
        if start_response.status_code == 200:
            print(f"✅ Session started successfully")
            total_passed += 1
        else:
            print(f"❌ Failed to start session")
        total_tests += 1
        
        # End session
        end_response = requests.post(f"{BASE_URL}/api/study/session/{session_id}/end", json={
            "focus_score": 85,
            "completed_goals": ["Test session workflow"],
            "notes": "Test completed successfully"
        })
        if end_response.status_code == 200:
            print(f"✅ Session ended successfully")
            total_passed += 1
        else:
            print(f"❌ Failed to end session")
        total_tests += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    success_rate = (total_passed / total_tests) * 100
    
    print(f"Tests completed: {total_passed}/{total_tests} passed ({success_rate:.1f}%)")
    
    if success_rate >= 95:
        print("🎉 EXCELLENT! All critical functionality working perfectly!")
        print("✅ Backend is production-ready")
        return True
    elif success_rate >= 80:
        print("✅ GOOD! Most functionality working correctly")
        print("⚠️  Some minor issues detected")
        return True
    elif success_rate >= 60:
        print("⚠️  PARTIAL! Core functionality working")
        print("🔧 Some features need attention")
        return False
    else:
        print("❌ CRITICAL ISSUES! Major functionality broken")
        print("🚨 Backend needs significant fixes")
        return False

def test_performance():
    """Test backend performance"""
    print(f"\n🔍 Performance Testing")
    print("=" * 40)
    
    # Test response times
    endpoints = [
        "/",
        "/api/status",
        "/api/study/sessions",
        "/api/study/analytics"
    ]
    
    for endpoint in endpoints:
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                if response_time < 100:
                    print(f"✅ {endpoint}: {response_time:.1f}ms (Excellent)")
                elif response_time < 500:
                    print(f"✅ {endpoint}: {response_time:.1f}ms (Good)")
                elif response_time < 1000:
                    print(f"⚠️  {endpoint}: {response_time:.1f}ms (Acceptable)")
                else:
                    print(f"❌ {endpoint}: {response_time:.1f}ms (Slow)")
            else:
                print(f"❌ {endpoint}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def main():
    print("Checking if backend is running...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not responding correctly")
            print("Make sure to run: python run.py")
            sys.exit(1)
    except:
        print("❌ Backend is not running!")
        print("Please start the backend first: python run.py")
        sys.exit(1)
    
    print("✅ Backend is running\n")
    
    # Run tests
    success = run_comprehensive_tests()
    
    # Performance tests
    test_performance()
    
    if success:
        print(f"\n🚀 Backend testing completed successfully!")
        print("You can now proceed with frontend integration!")
    else:
        print(f"\n🔧 Backend has issues that should be addressed")

if __name__ == "__main__":
    main()
