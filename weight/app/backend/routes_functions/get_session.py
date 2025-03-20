from flask import jsonify
import mysqlweight


def get_session(id):
    try:
        # Connect to database
        connection = mysqlweight.create_connection_with_retry()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        # Query to get session data
        session_query = """
            SELECT id, truck, direction, bruto, truckTara, neto, produce
            FROM transactions
            WHERE session = %s
            ORDER BY datetime
        """

        cursor.execute(session_query, (id,))
        session_records = cursor.fetchall()

        # Check if session exists
        if not session_records:
            return jsonify({"error": "Session not found"}), 404

        # Process the results
        # For simplicity, we'll use the first record for general info
        first_record = session_records[0]

        # Prepare the base response
        response = {
            "id": id,
            "truck": first_record["truck"] if first_record["truck"] else "na",
            "bruto": first_record["bruto"],
            "produce": first_record["produce"]
        }

        # Add OUT-specific fields if applicable
        out_record = next(
            (record for record in session_records if record["direction"] == "out"), None)
        if out_record:
            response["truckTara"] = out_record["truckTara"]
            response["neto"] = out_record["neto"] if out_record["neto"] is not None else "na"

        cursor.close()
        connection.close()

        return jsonify(response), 200

    except Exception as e:
        print(f"Error retrieving session: {e}")
        return jsonify({"error": str(e)}), 500
