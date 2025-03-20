import requests
import json
import sys


def run_get_session_check():
    BASE_URL = "http://127.0.0.1:5000"
    path = "session"

    checks = [
        {
            "id": "1",
            "expected": {
                "bruto": 16000,
                "id": "1",
                "neto": 3438,
                "truck": "test123",
                "truckTara": 12000,
                "produce": "orange",
            },
            "status": 200
        },
        {
            "id": "aaa",
            "expected": {},
            "status": 404
        }
    ]

    all_tests_passed = True

    for check in checks:
        expected = check["expected"]
        expected_status = check["status"]

        try:
            res = requests.get(f"{BASE_URL}/{path}/{check['id']}")

            if res.status_code == expected_status:
                try:
                    response_json = res.json()

                    missing_keys = [
                        key for key in expected.keys() if key not in response_json]
                    if missing_keys:
                        print(
                            f"❌ Test Failed: Missing keys {missing_keys} in response {response_json}")
                        all_tests_passed = False
                        sys.exit(1)
                        continue

                    mismatches = {
                        key: (response_json[key], expected[key])
                        for key in expected.keys()
                        if not (
                            isinstance(response_json[key], expected[key])
                            if isinstance(expected[key], type)
                            else response_json[key] == expected[key]
                        )
                    }

                    if mismatches:
                        print(
                            f"❌ Test Failed: Mismatched values {mismatches} in response {response_json}")
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

            if all_tests_passed:
                print("✅ All tests passed successfully!")

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test failed with exception: {e}")
            all_tests_passed = False
            sys.exit(1)
