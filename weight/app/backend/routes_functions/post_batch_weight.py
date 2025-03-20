from flask import request, jsonify
import mysqlweight
import os
import csv
import json


def post_batch_weight():
    upload_folder = "./in"

    file_name = request.get_json().get("file")
    file_path = os.path.join(upload_folder, file_name)

    containers = []

    if os.path.isfile(file_path):
        if file_name.endswith('.csv'):
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                unit = "kg" if "kg" in header[1].lower() else "lbs"
                for row in reader:
                    if len(row) == 2:
                        container_id, weight = row
                        containers.append(
                            (container_id, weight, unit))

        elif file_name.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                for entry in data:
                    containers.append(
                        (entry["id"], int(entry["weight"]), entry["unit"]))

        else:
            return jsonify({"error": f"Unsupported file format: {file_name}"}), 400

    if not containers:
        return jsonify({"error": "No valid files found"}), 400

    connection = mysqlweight.create_connection_with_retry()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    query = "INSERT INTO containers_registered (container_id, weight, unit) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE weight=VALUES(weight), unit=VALUES(unit)"
    cursor.executemany(query, containers)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Batch weight uploaded successfully", "count": len(containers)})
