import requests
import mysql.connector
import os
import sys

def connect():
  connection = None
  try:
    connection = mysql.connector.connect(
      host=os.environ.get('MYSQL_HOST', 'localhost'),
      port=3306,
      user=os.environ.get('MYSQL_USER', 'root'),
      password=os.environ.get('MYSQL_PASSWORD', 'rootpassword'),
      database="billdb"
    )
  except mysql.connector.Error as err:
    print(f"Error: '{err}'")
    raise

  return connection

def run_post_rates_check():
    
  # Dynamically construct the file path
  current_dir = os.path.dirname(os.path.abspath(__file__))
  rates_file_path = os.path.join(current_dir, "../../in/rates.xlsx")
  rates_file_path = os.path.abspath(rates_file_path)

  if not os.path.exists(rates_file_path):
      print(f"❌ File not found: {rates_file_path}")
      sys.exit(1)

  BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
  path = "rates"


  payload = {}
  headers = {}

  with open(rates_file_path, 'rb') as file:
    files = [
        ('file', ('rates.xlsx', file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        ]
    response = requests.request("POST", f"{BASE_URL}/{path}", headers=headers, data=payload, files=files)
  
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Rates")
    dbcount = cursor.fetchone()
    connection.commit()


    if response.status_code == 201 and dbcount[0] > 0:
        print("✅ POST Rates Check Passed")
    else:
        print(f"❌ POST Rates Check Failed: Status Code {response.status_code}, {dbcount[0]} rows in Rates table")
        sys.exit(1)