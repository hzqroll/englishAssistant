"""Test script for authentication and history API endpoints."""
import requests
import json
import sys
from typing import Optional

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(response: requests.Response, title: str = "Response"):
    """Print response details."""
    print(f"\n{title}:")
    print(f"  Status: {response.status_code}")
    try:
        data = response.json()
        print(f"  Data: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
    except:
        print(f"  Body: {response.text[:200]}")

def test_register() -> Optional[str]:
    """Test user registration."""
    print_section("Test 1: User Registration")

    url = f"{BASE_URL}/api/v1/auth/register"
    data = {
        "email": "test@example.com",
        "password": "testpass123",
        "tier": "free",
        "default_mode": "accuracy"
    }

    print(f"POST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        print_response(response, "Registration Response")

        if response.status_code == 201:
            print("✅ Registration successful!")
            return data["email"]
        elif response.status_code == 400 and "already registered" in response.text:
            print("⚠️  User already exists, proceeding with login")
            return data["email"]
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return None

def test_login(email: str) -> Optional[str]:
    """Test user login."""
    print_section("Test 2: User Login")

    url = f"{BASE_URL}/api/v1/auth/login"
    data = {
        "email": email,
        "password": "testpass123"
    }

    print(f"POST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        print_response(response, "Login Response")

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Login successful!")
            print(f"  Access Token: {token[:50]}...")
            print(f"  User ID: {data.get('user_id')}")
            print(f"  Tier: {data.get('tier')}")
            return token
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_get_current_user(token: str):
    """Test getting current user info."""
    print_section("Test 3: Get Current User Info")

    url = f"{BASE_URL}/api/v1/auth/me"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"GET {url}")
    print(f"Headers: Authorization: Bearer {token[:20]}...")

    try:
        response = requests.get(url, headers=headers)
        print_response(response, "User Info Response")

        if response.status_code == 200:
            print("✅ Get user info successful!")
            data = response.json()
            print(f"  Email: {data.get('email')}")
            print(f"  Tier: {data.get('tier')}")
            print(f"  Is Active: {data.get('is_active')}")
            return True
        else:
            print(f"❌ Get user info failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get user info error: {str(e)}")
        return False

def test_analyze_text(token: str) -> Optional[str]:
    """Test text analysis to create some history."""
    print_section("Test 4: Analyze Text (Create History)")

    url = f"{BASE_URL}/api/v1/analyze"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "text": "She dont like apples. He go to school yesterday.",
        "mode": "accuracy"
    }

    print(f"POST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data, headers=headers)
        print_response(response, "Analysis Response")

        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print("✅ Analysis successful!")
            print(f"  Analysis ID: {analysis_id}")
            print(f"  Errors Found: {len(result.get('errors', []))}")
            print(f"  Corrected Text: {result.get('corrected_text')[:100]}...")
            return analysis_id
        else:
            print(f"❌ Analysis failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        return None

def test_get_history(token: str):
    """Test getting analysis history."""
    print_section("Test 5: Get Analysis History")

    url = f"{BASE_URL}/api/v1/history"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"GET {url}")
    print(f"Headers: Authorization: Bearer {token[:20]}...")

    try:
        response = requests.get(url, headers=headers)
        print_response(response, "History Response")

        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print("✅ Get history successful!")
            print(f"  Total Items: {data.get('total')}")
            print(f"  Skip: {data.get('skip')}")
            print(f"  Limit: {data.get('limit')}")
            print(f"  First Item Preview: {json.dumps(items[0], indent=2)[:200] if items else 'No items'}...")
            return True
        else:
            print(f"❌ Get history failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get history error: {str(e)}")
        return False

def test_get_analysis_detail(token: str, analysis_id: str):
    """Test getting specific analysis detail."""
    print_section("Test 6: Get Analysis Detail")

    url = f"{BASE_URL}/api/v1/history/{analysis_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"GET {url}")
    print(f"Headers: Authorization: Bearer {token[:20]}...")

    try:
        response = requests.get(url, headers=headers)
        print_response(response, "Analysis Detail Response")

        if response.status_code == 200:
            data = response.json()
            print("✅ Get analysis detail successful!")
            print(f"  Original Text: {data.get('original_text')[:80]}...")
            print(f"  Corrected Text: {data.get('corrected_text')[:80]}...")
            print(f"  Mode: {data.get('mode')}")
            return True
        else:
            print(f"❌ Get analysis detail failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get analysis detail error: {str(e)}")
        return False

def test_delete_analysis(token: str, analysis_id: str):
    """Test deleting an analysis."""
    print_section("Test 7: Delete Analysis")

    url = f"{BASE_URL}/api/v1/history/{analysis_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"DELETE {url}")
    print(f"Headers: Authorization: Bearer {token[:20]}...")

    try:
        response = requests.delete(url, headers=headers)
        print_response(response, "Delete Response")

        if response.status_code == 200:
            print("✅ Delete analysis successful!")
            return True
        else:
            print(f"❌ Delete analysis failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Delete analysis error: {str(e)}")
        return False

def test_unauthorized_access():
    """Test that endpoints require authentication."""
    print_section("Test 8: Unauthorized Access (Should Fail)")

    url = f"{BASE_URL}/api/v1/history"

    print(f"GET {url} (no token)")

    try:
        response = requests.get(url)
        print_response(response, "Response")

        if response.status_code == 401:
            print("✅ Correctly requires authentication!")
            return True
        else:
            print(f"❌ Should have returned 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Authentication and History API Test Suite")
    print("="*60)

    # Test 1: Register user
    email = test_register()
    if not email:
        print("\n❌ Cannot proceed without registration")
        sys.exit(1)

    # Test 2: Login
    token = test_login(email)
    if not token:
        print("\n❌ Cannot proceed without login")
        sys.exit(1)

    # Test 3: Get current user
    test_get_current_user(token)

    # Test 4: Analyze text (create history)
    analysis_id = test_analyze_text(token)
    if not analysis_id:
        print("\n⚠️  Skipping history tests (no analysis created)")
        sys.exit(1)

    # Test 5: Get history
    test_get_history(token)

    # Test 6: Get analysis detail
    test_get_analysis_detail(token, analysis_id)

    # Test 7: Delete analysis
    test_delete_analysis(token, analysis_id)

    # Test 8: Unauthorized access
    test_unauthorized_access()

    print("\n" + "="*60)
    print("  Test Suite Complete!")
    print("="*60)

if __name__ == "__main__":
    main()
