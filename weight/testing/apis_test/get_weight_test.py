import requests
import json
from datetime import datetime, timedelta
import sys


def run_get_weight_check():
    BASE_URL = "http://127.0.0.1:5000"
    path = "weight"

    current_time = datetime.now()
    from_time = (current_time - timedelta(hours=12)).strftime("%Y%m%d%H%M%S")
    to_time = (current_time + timedelta(hours=12)).strftime("%Y%m%d%H%M%S")

    checks = [
        {
            "payload": {
                "from": from_time,
                "to": to_time,
                "filter": "in,out"
            },
            "expected": [
                {
                    "bruto": 16000,
                    "containers": ["C-35434", "K-4109"],
                    "direction": "in",
                    "id": int,
                    "neto": None,
                    "produce": "orange"
                },
                {
                    "bruto": 16000,
                    "containers": ["C-35434", "K-4109"],
                    "direction": "out",
                    "id": int,
                    "neto": 3438,
                    "produce": "orange"
                },
                {
                    "bruto": 22222,
                    "containers": ["C-35434", "cacacaca"],
                    "direction": "in",
                    "id": int,
                    "neto": None,
                    "produce": "orange"
                },
                {
                    "bruto": 22222,
                    "containers": ["C-35434", "cacacaca"],
                    "direction": "out",
                    "id": int,
                    "neto": None,
                    "produce": "orange"
                }
            ],
            "status": 200
        },
        {
            "payload": {
                "from": from_time,
                "to": to_time,
                "filter": "in"
            },
            "expected": [
                {
                    "bruto": 16000,
                    "containers": ["C-35434", "K-4109"],
                    "direction": "in",
                    "id": int,
                    "neto": None,
                    "produce": "orange"
                },
                {
                    "bruto": 22222,
                    "containers": ["C-35434", "cacacaca"],
                    "direction": "in",
                    "id": int,
                    "neto": None,
                    "produce": "orange"
                },
            ],
            "status": 200
        },
        {
            "payload": {
                "from": from_time,
                "to": to_time,
                "filter": "out"
            },
            "expected": [
                {
                    "bruto": 16000,
                    "containers": ["C-35434", "K-4109"],
                    "direction": "out",
                    "id": int,
                    "neto": 3438,
                    "produce": "orange"
                },
                {
                    "bruto": 22222,
                    "containers": ["C-35434", "cacacaca"],
                    "direction": "out",
                    "id": int,
                    "neto": None,
                    "produce": "orange"
                }
            ],
            "status": 200
        },
        {
            "payload": {
                "from": 19990309084418,
                "to": 19990309084418,
                "filter": "in,out"
            },
            "expected": [],
            "status": 200
        }
    ]

    all_tests_passed = True
    for check in checks:
        payload = check["payload"]
        expected = check["expected"]
        expected_status = check["status"]

        try:
            res = requests.get(f"{BASE_URL}/{path}", params=payload)

            if res.status_code == expected_status:
                try:
                    response_json = res.json()

                    if isinstance(response_json, list):
                        if len(response_json) > len(expected):
                            print(
                                f"❌ Test Failed: Received more items than expected. Expected {len(expected)}, but got {len(response_json)}")
                            all_tests_passed = False
                            sys.exit(1)
                            continue

                        for i, expected_item in enumerate(expected):
                            response_item = response_json[i]

                            mismatches = {
                                key: (response_item[key], expected_item[key])
                                for key in expected_item.keys()
                                if not (
                                    isinstance(
                                        response_item[key], expected_item[key])
                                    if isinstance(expected_item[key], type)
                                    else response_item[key] == expected_item[key]
                                )
                            }

                            if mismatches:
                                print(
                                    f"❌ Test Failed: Mismatched values \n res:{response_item} \n exp:{response_json} for item {i}")
                                all_tests_passed = False
                                sys.exit(1)

                    else:
                        print("❌ Test Failed: Response is not a list")
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
                print(f"✅ All tests passed successfully! : {payload}")

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test failed with exception: {e}")
            all_tests_passed = False
            sys.exit(1)
