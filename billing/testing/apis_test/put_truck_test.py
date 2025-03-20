import requests
import os
import json
import sys

def run_put_truck_check():
    BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
    
    # Create two providers for testing
    provider1_res = requests.post(
        f"{BASE_URL}/provider",
        json={"name": "Provider1ForTruck"}
    )
    
    provider2_res = requests.post(
        f"{BASE_URL}/provider",
        json={"name": "Provider2ForTruck"}
    )
    
    if provider1_res.status_code != 201 or provider2_res.status_code != 201:
        print(f"❌ Test setup failed: Could not create test providers")
        sys.exit(1)
    
    provider1_id = provider1_res.json()["id"]
    provider2_id = provider2_res.json()["id"]
    
    # Create a truck for testing
    truck_res = requests.post(
        f"{BASE_URL}/truck",
        json={"id": "TEST123", "provider_id": provider1_id}
    )
    
    if truck_res.status_code != 201:
        print(f"❌ Test setup failed: Could not create test truck")
        sys.exit(1)

    checks = [
        {
            "id": "TEST123",
            "payload": {
                "provider_id": provider2_id
            },
            "expected": {
                "message": "Truck updated successfully"
            },
            "status": 200
        },
        {
            "id": "NONEXISTENT",
            "payload": {
                "provider_id": provider1_id
            },
            "expected": {
                "error": str
            },
            "status": 404
        },
        {
            "id": "TEST123",
            "payload": {
                "provider_id": "999999"  # Non-existent provider
            },
            "expected": {
                "error": str
            },
            "status": 400
        },
        {
            "id": "TEST123",
            "payload": {},
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
        truck_id = check["id"]

        try:
            res = requests.put(
                f"{BASE_URL}/truck/{truck_id}",
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
                        sys.exit(1)

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