import requests
from app.mysqlbilling import connect

link="http://127.0.0.1:5001"
path="provider"
id=10004
name="Bezeq"

try:
    res = requests.post(f'{link}/{path}', json={"name":f"{name}"})
    resp = res.json()
    print(resp, res.status_code)
except Exception as e:
    print(f"Test failed with exception: {e}")

try:
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Provider WHERE name = %s", (name,))
    whole_line = cursor.fetchall()
    for i in whole_line:
        print(i[0], i[1])
    cursor.close()
    connection.close()
except Exception as e:
    print(f"Test failed with exception: {e}")


try:
    res = requests.put(f'{link}/{path}/{id}', json={"name":f"{name}"})
    resp = res.json()
    print(resp, res.status_code)
except Exception as e:
    print(f"Test failed with exception: {e}")

try:
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Provider WHERE name = %s", (name,))
    whole_line = cursor.fetchall()
    for i in whole_line:
        print(i[0], i[1])
    cursor.close()
    connection.close()
except Exception as e:
    print(f"Test failed with exception: {e}")

def test_health_check():
    response = requests.get(f"{link}/health")
    try:
        assert response.status_code == 20
    except AssertionError as e:
        print(f"AssertionError-HealthStatusCode")
    try:
        assert response.text == "OK"
    except AssertionError as e:
        print(f"AssertionError-HealthResponse")

test_health_check()