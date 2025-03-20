import requests
import os
import io
import pandas as pd
import sys

def run_get_rates_check():
    BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
    path = "rates"

    all_tests_passed = True

    try:
        res = requests.get(f"{BASE_URL}/{path}")
        expected_status = 200

        if res.status_code == expected_status:
            # Check if response is a file download
            if 'Content-Disposition' in res.headers and 'attachment' in res.headers['Content-Disposition']:
                # Check if the filename ends with .xlsx
                content_disposition = res.headers['Content-Disposition']
                if 'rates.xlsx' not in content_disposition:
                    print("❌ Test Failed: Expected 'rates.xlsx' in Content-Disposition header")
                    print(f"Content-Disposition: {content_disposition}")
                    all_tests_passed = False
                    sys.exit(1)
                
                # Try to read the content as an Excel file
                try:
                    # Create a BytesIO object from the response content
                    excel_file = io.BytesIO(res.content)
                    
                    # Try to read it as an Excel file
                    df = pd.read_excel(excel_file)
                    
                    # Check if required columns exist
                    required_columns = {"Product", "Rate", "Scope"}
                    if not required_columns.issubset(set(df.columns)):
                        print(f"❌ Test Failed: Excel file is missing required columns. Found: {df.columns}")
                        all_tests_passed = False
                        sys.exit(1)
                    else:
                        print("✅ Excel file format verification passed")
                        
                except Exception as e:
                    print(f"❌ Test Failed: Content is not a valid Excel file: {str(e)}")
                    all_tests_passed = False
                    sys.exit(1)
            else:
                print("❌ Test Failed: Expected file download response")
                all_tests_passed = False
                sys.exit(1)
        else:
            print(f"❌ Test Failed: Expected status {expected_status}, but got {res.status_code}")
            if res.headers.get('Content-Type') == 'application/json':
                try:
                    print(f"Response: {res.json()}")
                except:
                    print(f"Response: {res.text}")
            all_tests_passed = False
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"🚨 Test failed with exception: {e}")
        all_tests_passed = False
        sys.exit(1)

    if all_tests_passed:
        print("✅ All rates tests passed successfully!")