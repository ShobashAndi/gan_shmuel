import requests
import json
import os
import sys

def run_put_provider_check():
    BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
    path = "provider"

    # Create a provider first to get a valid ID
    setup_res = requests.post(
        f"{BASE_URL}/{path}",
        json={"name": "ProviderToUpdate"}
    )
    
    if setup_res.status_code != 201:
        print(f"❌ Test setup failed: Could not create test provider / provider exists")
        sys.exit(1)
    
    provider_id = setup_res.json()["id"]

    checks = [
        {
            "id": provider_id,
            "payload": {
                "name": "UpdatedProvider"
            },
            "expected": {
                "message": "Provider updated successfully"
            },
            "status": 200
        },
        {
            "id": "999999",  # Non-existent ID
            "payload": {
                "name": "UpdatedProvider"
            },
            "expected": {
                "error": str
            },
            "status": 404
        },
        {
            "id": provider_id,
            "payload": {},
            "expected": {
                "error": str
            },
            "status": 400
        },
        {
            "id": "invalid",  # Invalid ID format
            "payload": {
                "name": "UpdatedProvider"
            },
            "expected": {
                "error": str
            },
            "status": 400
        }
    ]

    all_tests_passed = True

    for check in checks:
        payload = check["payload"]
        expected = check["expected"]
        expected_status = check["status"]
        provider_id = check["id"]

        try:
            res = requests.put(
                f"{BASE_URL}/{path}/{provider_id}",
                json=payload
            )

            if res.status_code == expected_status:
                try:
                    response_json = res.json()

                    missing_keys = [
                        key for key in expected.keys() if key not in response_json]
                    if missing_keys:
                        print(
                            f"❌ Test Failed: Missing keys {missing_keys} in response {response_json}")
                        all_tests_passed = False
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

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test failed with exception: {e}")
            all_tests_passed = False
            sys.exit(1)

    if all_tests_passed:
        print("✅ All tests passed successfully!")