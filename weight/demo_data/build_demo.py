import json
import os
import random
import requests
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import app.backend.mysqlweight as mysqlweight

BASE_URL = "http://127.0.0.1:5000"
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
input_trucks = os.path.join(DATA_DIR, "trucks.json")
input_containers = os.path.join(DATA_DIR, "containers.json")

produces = ["Navel", "Blood", "Shamuti", "Tangerine",
            "Clementine", "Grapefruit", "Valencia", "Mandarin"]


def convert_to_kg(weight, unit):
    return weight * 0.453592 if unit == "lbs" else weight


def get_random_containers(containers):
    selected_containers = random.sample(containers, random.randint(1, 3))
    return ",".join(container["id"] for container in selected_containers)


def get_random_produce():
    return random.choice(produces)


def calculate_random_weight(truck, containers_on_truck, all_containers):
    truck_weight_kg = convert_to_kg(truck["weight"], truck["unit"])

    containers_weight = sum(
        convert_to_kg(container["weight"], container["unit"]) for container in all_containers if container["id"] in containers_on_truck
    )
    produce_weight = random.randint(100, 500)
    total_weight = truck_weight_kg + containers_weight + produce_weight

    return total_weight


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


def post_batch_weight():
    path = "batch-weight"
    requests.post(f"{BASE_URL}/{path}", json={"file": "containers1.csv"})
    requests.post(f"{BASE_URL}/{path}", json={"file": "containers2.csv"})


def post_truck(payload):
    path = "weight"
    requests.post(f"{BASE_URL}/{path}", json=payload)


def process_trucks():
    with open(input_trucks, "r", encoding="utf-8") as file:
        trucks = json.load(file)

    with open(input_containers, "r", encoding="utf-8") as file:
        containers = json.load(file)

    for truck in trucks:
        rand_containers = get_random_containers(containers)
        rand_produce = get_random_produce()

        total_weight_in = calculate_random_weight(
            truck, rand_containers, containers)
        truck_in = {
            "direction": "in",
            "truck": truck["id"],
            "containers": rand_containers,
            "weight": total_weight_in,
            "unit": "kg",
            "force": False,
            "produce": rand_produce
        }
        truck_out = {
            "direction": "out",
            "truck": truck["id"],
            "weight": truck["weight"],
            "unit": truck["unit"],
            "force": False,
        }
        post_truck(truck_in)
        post_truck(truck_out)


if __name__ == "__main__":
    clear_mysql_tables()
    post_batch_weight()
    process_trucks()
    print("Insert demo data to database tables")
