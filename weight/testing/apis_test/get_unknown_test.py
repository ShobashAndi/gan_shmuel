import requests
import json
import sys


def run_get_unknown_check():
    BASE_URL = "http://127.0.0.1:5000"
    path = "unknown"

    checks = [
        {
            "expected": [
                "cacacaca"
            ],
            "status": 200
        }
    ]

    all_tests_passed = True

    for check in checks:
        expected = check["expected"]
        expected_status = check["status"]

        try:
            res = requests.get(f"{BASE_URL}/{path}")

            if res.status_code == expected_status:
                try:
                    response_json = res.json()

                    if response_json != expected:
                        print(
                            f"❌ Test Failed: Expected {expected}, but got {response_json}")
                        all_tests_passed = False
                        sys.exit(1)

                except json.JSONDecodeError:
                    print(
                        f"❌ Test Failed: Response is not valid JSON -> {res.text}")
                    all_tests_passed = False
                    sys.exit(1)

            else:
                print(
                    f"❌ Test Failed: Expected status {expected_status}, but got {res.status_code}")
                all_tests_passed = False
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test failed with exception: {e}")
            all_tests_passed = False
            sys.exit(1)

    if all_tests_passed:
        print("✅ All tests passed successfully!")
