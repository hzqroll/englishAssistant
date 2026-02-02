#!/usr/bin/env python3
"""Test history API."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Login
response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": "testuser@example.com",
    "password": "testpass123"
})

if response.status_code != 200:
    print(f"Login failed: {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()
token = data.get("access_token")
print(f"✅ Login successful")
print(f"Token: {token[:30]}...")

# Test history endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/v1/history", headers=headers)

print(f"\n📊 History endpoint status: {response.status_code}")

if response.status_code == 200:
    history = response.json()
    print(f"✅ History successful!")
    print(f"  Number of items: {len(history)}")
    if history:
        print(f"  First item: {json.dumps(history[0], indent=2)[:200]}...")
else:
    print(f"❌ History failed: {response.text}")

# Test analyze to create history
print("\n🔍 Creating analysis...")
response = requests.post(f"{BASE_URL}/api/v1/analyze",
    json={"text": "Testing history API", "mode": "accuracy"},
    headers=headers)

if response.status_code == 200:
    analysis = response.json()
    analysis_id = analysis.get("analysis_id")
    print(f"✅ Analysis created: {analysis_id}")

    # Test get analysis detail
    response = requests.get(f"{BASE_URL}/api/v1/history/{analysis_id}", headers=headers)
    if response.status_code == 200:
        print(f"✅ Get analysis detail successful")
    else:
        print(f"❌ Get detail failed: {response.status_code}")
else:
    print(f"❌ Analysis failed: {response.status_code}")

# Test history again (should have items now)
response = requests.get(f"{BASE_URL}/api/v1/history", headers=headers)

if response.status_code == 200:
    history = response.json()
    print(f"\n📊 Updated history: {len(history)} items")
    if history:
        print(f"  Latest: {history[0].get('original_text', '')[:50]}...")
