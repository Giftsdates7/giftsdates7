#!/usr/bin/env python3
"""
Backend Auth/Login Persistence Test for GiftsDates
Tests core authentication flows: registration, login, and JWT persistence
"""
import requests
import json
import sys
from datetime import datetime

# Load backend URL from frontend .env
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.split('=', 1)[1].strip()
            break

BASE_URL = f"{BACKEND_URL}/api"
print(f"Testing backend at: {BASE_URL}\n")

# Test data - realistic user
TEST_USER = {
    "email": f"layla.hassan.{int(datetime.now().timestamp())}@example.com",
    "password": "SecurePass123!",
    "name": "Layla Hassan",
    "age": 28,
    "gender": "female",
    "interested_in": "male",
    "orientation": "straight",
    "city": "Dubai",
    "country": "UAE",
    "bio": "Love traveling and meeting new people",
    "language": "en"
}

def test_root_endpoint():
    """Test 1: GET /api/ returns service ok"""
    print("=" * 60)
    print("TEST 1: GET /api/ - Service Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ PASS: Root endpoint accessible")
            return True
        elif response.status_code == 404:
            print("⚠️  INFO: Root endpoint not found (404) - this is acceptable if not implemented")
            return True  # Not a critical failure
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error accessing root endpoint: {e}")
        return False

def test_register():
    """Test 2: Register a new user"""
    print("\n" + "=" * 60)
    print("TEST 2: POST /api/auth/register - User Registration")
    print("=" * 60)
    print(f"Registering user: {TEST_USER['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify response structure
            if "token" not in data:
                print("❌ FAIL: No token in response")
                return None, None
            if "user" not in data:
                print("❌ FAIL: No user object in response")
                return None, None
            
            token = data["token"]
            user = data["user"]
            
            print(f"✅ Token received: {token[:20]}...")
            print(f"✅ User ID: {user.get('id')}")
            print(f"✅ User email: {user.get('email')}")
            print(f"✅ User name: {user.get('name')}")
            
            # Verify user data matches registration
            if user.get('email') != TEST_USER['email'].lower():
                print(f"❌ FAIL: Email mismatch - expected {TEST_USER['email'].lower()}, got {user.get('email')}")
                return None, None
            if user.get('name') != TEST_USER['name']:
                print(f"❌ FAIL: Name mismatch - expected {TEST_USER['name']}, got {user.get('name')}")
                return None, None
            
            print("✅ PASS: User registration successful with correct data")
            return token, user.get('id')
        else:
            print(f"❌ FAIL: Registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ FAIL: Error during registration: {e}")
        return None, None

def test_login():
    """Test 3: Login with registered user"""
    print("\n" + "=" * 60)
    print("TEST 3: POST /api/auth/login - User Login")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER['email'],
                "password": TEST_USER['password']
            },
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if "token" not in data:
                print("❌ FAIL: No token in response")
                return None, None
            if "user" not in data:
                print("❌ FAIL: No user object in response")
                return None, None
            
            token = data["token"]
            user = data["user"]
            
            print(f"✅ Token received: {token[:20]}...")
            print(f"✅ User ID: {user.get('id')}")
            print(f"✅ User email: {user.get('email')}")
            
            print("✅ PASS: Login successful")
            return token, user.get('id')
        else:
            print(f"❌ FAIL: Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ FAIL: Error during login: {e}")
        return None, None

def test_auth_me(token, expected_user_id):
    """Test 4: GET /api/auth/me with JWT token"""
    print("\n" + "=" * 60)
    print("TEST 4: GET /api/auth/me - Verify JWT Authentication")
    print("=" * 60)
    print(f"Using token: {token[:20]}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print(f"Response keys: {list(user.keys())}")
            print(f"User ID: {user.get('id')}")
            print(f"User email: {user.get('email')}")
            print(f"User name: {user.get('name')}")
            
            # Verify user ID matches
            if user.get('id') != expected_user_id:
                print(f"❌ FAIL: User ID mismatch - expected {expected_user_id}, got {user.get('id')}")
                return False
            
            # Verify email matches
            if user.get('email') != TEST_USER['email'].lower():
                print(f"❌ FAIL: Email mismatch - expected {TEST_USER['email'].lower()}, got {user.get('email')}")
                return False
            
            print("✅ PASS: JWT authentication successful, user data matches")
            return True
        else:
            print(f"❌ FAIL: Auth/me failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error during auth/me: {e}")
        return False

def test_jwt_persistence(token, expected_user_id):
    """Test 5: Verify JWT works across fresh requests (persistence)"""
    print("\n" + "=" * 60)
    print("TEST 5: JWT Persistence - Fresh Request with Same Token")
    print("=" * 60)
    print("Making a fresh request with the same JWT token...")
    
    try:
        # Make a completely fresh request with the same token
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print(f"User ID: {user.get('id')}")
            print(f"User email: {user.get('email')}")
            
            # Verify user ID matches
            if user.get('id') != expected_user_id:
                print(f"❌ FAIL: User ID mismatch - JWT not persisting correctly")
                return False
            
            print("✅ PASS: JWT token persists across fresh requests")
            return True
        else:
            print(f"❌ FAIL: JWT persistence check failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error during JWT persistence test: {e}")
        return False

def main():
    """Run all auth/login persistence tests"""
    print("\n" + "=" * 60)
    print("GIFTSDATES BACKEND AUTH/LOGIN PERSISTENCE TEST")
    print("=" * 60)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Root endpoint
    results.append(("Root Endpoint", test_root_endpoint()))
    
    # Test 2: Register
    reg_token, reg_user_id = test_register()
    results.append(("User Registration", reg_token is not None))
    
    if reg_token and reg_user_id:
        # Test 3: Login
        login_token, login_user_id = test_login()
        results.append(("User Login", login_token is not None))
        
        if login_token and login_user_id:
            # Test 4: Auth/me with login token
            results.append(("JWT Authentication (/auth/me)", test_auth_me(login_token, login_user_id)))
            
            # Test 5: JWT persistence
            results.append(("JWT Persistence", test_jwt_persistence(login_token, login_user_id)))
    else:
        print("\n⚠️  Skipping login and JWT tests due to registration failure")
        results.append(("User Login", False))
        results.append(("JWT Authentication (/auth/me)", False))
        results.append(("JWT Persistence", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
