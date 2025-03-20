import apis_test.get_health_test
import apis_test.post_provider_test
import apis_test.put_provider_test
import apis_test.post_truck_test
import apis_test.put_truck_test
import apis_test.get_truck_test
import apis_test.post_rates_test
import apis_test.get_rates_test
import apis_test.get_bill_test

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.mysqlbilling import connect

def clear_mysql_tables():
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE Provider;")
        cursor.execute("TRUNCATE TABLE Rates;")
        cursor.execute("TRUNCATE TABLE Trucks;")
        connection.commit()
        cursor.close()
        connection.close()
        print("Database tables cleared successfully.")
    except Exception as e:
        print(f"Error clearing database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        clear_mysql_tables()
    
        print('get health check')
        apis_test.get_health_test.run_health_check()
      
        print('post provider check')
        apis_test.post_provider_test.run_post_provider_check()
    
        print('put provider check')
        apis_test.put_provider_test.run_put_provider_check()
        
        print('post truck check')
        apis_test.post_truck_test.run_post_truck_check()
     
        print('put truck check')
        apis_test.put_truck_test.run_put_truck_check()

        print('get truck check')
        apis_test.get_truck_test.run_get_truck_check()

        print('post rates check')
        apis_test.post_rates_test.run_post_rates_check()

        print('get rates check')
        apis_test.get_rates_test.run_get_rates_check()

        print('get bill check')
        apis_test.get_bill_test.run_get_bill_check()

        print("🎉 All tests passed successfully!")

    except Exception as e:
        sys.exit(1)