from flask import request, jsonify
from datetime import datetime
import mysqlweight
import mysql.connector
import json


def get_weight(paramFrom, paramTo):
    
    # Convert paramFrom and paramTo to MySQL DATETIME format
    try:
        paramFromFormatted = datetime.strptime(
            paramFrom, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        paramToFormatted = datetime.strptime(
            paramTo, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected format: yyyymmddhhmmss"}), 400

    paramFilter = request.args.get("filter", "in,out,none")

    filterList = tuple(paramFilter.split(","))

    try:
        connection = mysqlweight.connect()
        # Enables fetching rows as dictionaries
        cursor = connection.cursor(dictionary=True)

        query = """
                SELECT id, direction, bruto, neto, produce, containers, session
                FROM transactions
                WHERE direction IN ({})
                AND datetime BETWEEN %s AND %s
            """.format(",".join(["%s"] * len(filterList)))

        # SQL Query to fetch required columns
        cursor.execute(
            query, (*filterList, paramFromFormatted, paramToFormatted))
        transactions = cursor.fetchall()

        # Convert `containers` column from string to list
        for transaction in transactions:
            if transaction["containers"]:  # Ensure it's not None
                transaction["containers"] = json.loads(
                    transaction["containers"])

        cursor.close()
        connection.close()

        return jsonify(transactions), 200

    except mysql.connector.Error as err:
        return jsonify({"error xx": str(err)}), 500
