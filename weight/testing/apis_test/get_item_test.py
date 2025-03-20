import requests
import json
import sys
from datetime import datetime, timedelta


def run_get_item_check():
    BASE_URL = "http://127.0.0.1:5000"
    path = "item"

    current_time = datetime.now()
    from_time = (current_time - timedelta(hours=12)).strftime("%Y%m%d%H%M%S")
    to_time = (current_time + timedelta(hours=12)).strftime("%Y%m%d%H%M%S")

    checks = [
        {
            "id": "test123",
            "payload": {
                "from": from_time,
                "to": to_time
            },
            "expected": {
                "id": "test123",
                "sessions": [1],
                "tara": 12000
            },
            "status": 200
        },
        {
            "id": "test123",
            "payload": {
                "from": 19990309084418,
                "to": 19990309084418
            },
            "expected": {},
            "status": 404
        },
        {
            "id": "test78",
            "payload": {
                "from": 19990309084418,
                "to": 19990309084418
            },
            "expected": {},
            "status": 404
        },
    ]

    all_tests_passed = True

    for check in checks:
        payload = check["payload"]
        expected = check["expected"]
        expected_status = check["status"]

        try:
            res = requests.get(
                f"{BASE_URL}/{path}/{check['id']}?from={payload['from']}&to={payload['to']}")

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
