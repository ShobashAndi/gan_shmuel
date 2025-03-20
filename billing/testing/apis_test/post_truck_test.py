import requests
import os
import json
import sys

def run_post_truck_check():
    BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
    path = "truck"
    
    # Create a provider for testing
    provider_res = requests.post(
        f"{BASE_URL}/provider",
        json={"name": "ProviderForTruckTESTING"}
    )
    
    if provider_res.status_code != 201:
        print(f"❌ Test setup failed: Could not create test provider")
        sys.exit(1)
    
    provider_id = provider_res.json()["id"]

    checks = [
        {
            "payload": {
                "id": "ABC123",
                "provider_id": provider_id
            },
            "expected": {
                "message": "Truck registered successfully",
                "id": "ABC123"
            },
            "status": 201
        },
        {
            "payload": {
                "id": "ABC123",  # Duplicate ID
                "provider_id": provider_id
            },
            "expected": {
                "error": str
            },
            "status": 409
        },
        {
            "payload": {
                "id": "DEF456",
                "provider_id": "999999"  # Non-existent provider
            },
            "expected": {
                "error": str
            },
            "status": 404
        },
        {
            "payload": {
                "provider_id": provider_id
                # Missing 'id' field
            },
            "expected": {
                "error": str
            },
            "status": 400
        },
        {
            "payload": {
                "id": "GHI789"
                # Missing 'provider_id' field
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

        try:
            res = requests.post(
                f"{BASE_URL}/{path}",
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