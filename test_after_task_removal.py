#!/usr/bin/env python3
"""
Test script to verify all endpoints work after task removal
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Test user credentials (you'll need to update with a valid token)
AUTH_TOKEN = None


def test_endpoint(method, endpoint, data=None, auth=True):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if auth and AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            response = requests.post(url, headers=headers, json=data)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)


def main():
    print("Testing Green Moment API after task removal...")
    print("=" * 50)
    
    # First, try to get a token (anonymous login for testing)
    print("\n1. Testing anonymous login...")
    success, result = test_endpoint("POST", "/auth/anonymous", auth=False)
    if success:
        print("✅ Anonymous login successful")
        global AUTH_TOKEN
        AUTH_TOKEN = result.get("access_token")
    else:
        print(f"❌ Anonymous login failed: {result}")
        sys.exit(1)
    
    # Test progress endpoint (should no longer have tasks)
    print("\n2. Testing progress summary...")
    success, result = test_endpoint("GET", "/progress/summary")
    if success:
        print("✅ Progress summary successful")
        # Check that task fields are removed
        if "current_month_tasks" in result:
            print("❌ ERROR: Task fields still present in response!")
        else:
            print("✅ Task fields properly removed")
        print(f"   Current league: {result.get('current_league')}")
        print(f"   Carbon saved: {result.get('current_month_co2e_saved_g')}g")
    else:
        print(f"❌ Progress summary failed: {result}")
    
    # Test that task endpoints are removed
    print("\n3. Testing that task endpoints are removed...")
    success, result = test_endpoint("GET", "/tasks")
    if not success and "404" in str(result):
        print("✅ Task endpoint properly removed (404)")
    else:
        print(f"❌ Task endpoint still accessible: {result}")
    
    # Test chores endpoint still works
    print("\n4. Testing chores endpoint...")
    success, result = test_endpoint("GET", "/chores")
    if success:
        print("✅ Chores endpoint working")
    else:
        print(f"❌ Chores endpoint failed: {result}")
    
    # Test carbon endpoint
    print("\n5. Testing carbon intensity endpoint...")
    success, result = test_endpoint("GET", "/carbon/current")
    if success:
        print("✅ Carbon intensity endpoint working")
        print(f"   Current intensity: {result.get('carbon_intensity_gco2e_kwh')}g CO2e/kWh")
    else:
        print(f"❌ Carbon intensity endpoint failed: {result}")
    
    # Test league info endpoint
    print("\n6. Testing league info endpoint...")
    success, result = test_endpoint("GET", "/progress/league")
    if success:
        print("✅ League info endpoint working")
        if "tasks_required" in result or "tasks_completed" in result:
            print("❌ ERROR: Task fields still present in league response!")
        else:
            print("✅ Task fields properly removed from league info")
    else:
        print(f"❌ League info endpoint failed: {result}")
    
    # Test user profile
    print("\n7. Testing user profile...")
    success, result = test_endpoint("GET", "/users/me")
    if success:
        print("✅ User profile endpoint working")
        print(f"   Username: {result.get('username')}")
        print(f"   League: {result.get('current_league')}")
    else:
        print(f"❌ User profile endpoint failed: {result}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")


if __name__ == "__main__":
    main()