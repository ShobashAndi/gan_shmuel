from flask import jsonify
from datetime import datetime
import mysqlweight


def get_item(id, paramFrom, paramTo):
    try:
        paramFromFormatted = datetime.strptime(
            paramFrom, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        paramToFormatted = datetime.strptime(
            paramTo, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected format: yyyymmddhhmmss"}), 400

    connection = mysqlweight.connect()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT * FROM transactions 
        WHERE (truck = %s OR JSON_CONTAINS(containers, JSON_QUOTE(%s)))
        AND datetime BETWEEN %s AND %s
    """

    cursor.execute(query, (id, id, paramFromFormatted, paramToFormatted))
    transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    if not transactions:
        return jsonify({"error": "No transactions found"}), 404

    sessions = set()
    tara = "na"

    for record in transactions:
        sessions.add(record["session"])
        if record["truckTara"]:
            tara = record["truckTara"]

    return jsonify({
        "id": id,
        "tara": tara,
        "sessions": list(sessions)
    }), 200
