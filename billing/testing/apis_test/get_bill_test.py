import requests
import os
import sys


def run_get_bill_check():
    BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
    path = "bill"
    id = 6

    bill_get_url = f"{BASE_URL}/{path}/{id}"
    try:
        response = requests.get(bill_get_url)
        if response.status_code == 200:
            get_bill = ("✅ Bill GET Test Passed")
            print(get_bill)
        else:
            get_bill = ("❌ Bill GET Test FAILED!")
            print(get_bill, response.status_code)
            sys.exit(1)
    except requests.RequestException as e:
        get_bill = ("❌ Bill GET Test FAILED!")
        print(get_bill, e)
        sys.exit(1)