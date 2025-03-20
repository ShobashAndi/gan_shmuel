import mysql.connector
import os

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
    print("MySQL Database connection successful")
  except mysql.connector.Error as err:
    print(f"Error: '{err}'")
    raise

  return connection
