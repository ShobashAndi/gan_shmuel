from flask import jsonify
import mysqlweight
import mysql.connector
import json


def get_unknown():
    try:
        connection = mysqlweight.connect()
        # Enables fetching rows as dictionaries
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT direction, neto, containers
            FROM transactions
            WHERE direction = %s AND neto IS %s 
        """

        # SQL Query to fetch required columns

        cursor.execute(query, ("out", None))
        transactions = cursor.fetchall()

        container_ids = set()

        for transaction in transactions:
            for container in json.loads(transaction["containers"]):
                container_ids.add(container)

        if not container_ids:
            return jsonify([])

        # return jsonify({"len": len(container_ids)}), 200

        query = f"""
            SELECT container_id 
            FROM ({" UNION ALL ".join(["SELECT %s AS container_id"] * len(container_ids))}) AS input_list
            WHERE container_id NOT IN (SELECT container_id FROM containers_registered);
        """

        cursor.execute(query, list(container_ids))

        missing_ids = [row["container_id"] for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        return jsonify(missing_ids), 200

    except mysql.connector.Error as err:
        return jsonify({"error xx": str(err)}), 500
