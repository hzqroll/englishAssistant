"""Test script for analyze endpoint."""
import requests
import traceback
import sys

def test_analyze():
    """Test the analyze endpoint."""
    try:
        url = "http://localhost:8000/api/v1/analyze"
        data = {
            "text": "She dont like apples.",
            "mode": "accuracy"
        }

        print(f"Sending POST request to {url}")
        print(f"Data: {data}")

        response = requests.post(url, json=data)

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            print("\n✅ SUCCESS!")
            return True
        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            return False

    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analyze()
    sys.exit(0 if success else 1)
