import requests
import os
import sys

def run_health_check():

    BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
    path = "health"

    try:
        res = requests.get(f"{BASE_URL}/{path}")
        expected_text = "OK"
        expected_status = 200

        if res.status_code == expected_status and res.text.strip() == expected_text:
            print("✅ Health Check Passed")
        else:
            print(
                f"❌ Health Check Failed: Expected '{expected_text}, {expected_status}', but got '{res.text.strip()}, {res.status_code}'")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"🚨 Test failed with exception: {e}")
        sys.exit(1)
