import apis_test.get_health_test
import apis_test.post_batch_weight_test
import apis_test.post_weight_test
import apis_test.get_weight_test
import apis_test.get_item_test
import apis_test.get_session_test
import apis_test.get_unknown_test

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import app.backend.mysqlweight as mysqlweight


def clear_mysql_tables():
    try:
        connection = mysqlweight.connect()
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE transactions;")
        cursor.execute("TRUNCATE TABLE containers_registered;")
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
        
        # api test
        # get health check
        print('get health check')
        apis_test.get_health_test.run_health_check()

        # post batch weight check
        print('post batch weight check')
        apis_test.post_batch_weight_test.run_batch_weight_check()

        # post weight check
        print('post weight check')
        apis_test.post_weight_test.run_post_weight_check()

        # get weight check
        print('get weight check')
        apis_test.get_weight_test.run_get_weight_check()

        # get item check
        print('get item check')
        apis_test.get_item_test.run_get_item_check()

        #  get session check
        print('get session check')
        apis_test.get_session_test.run_get_session_check()

        # get unknown check
        print('get unknown check')
        apis_test.get_unknown_test.run_get_unknown_check()

        print("🎉 All tests passed successfully!")
    except Exception as e:
        sys.exit(1)
