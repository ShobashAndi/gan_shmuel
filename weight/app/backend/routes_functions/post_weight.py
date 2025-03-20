from flask import request, jsonify
from datetime import datetime
import mysqlweight
import json
from utility import convert_to_kg 

def handle_weight_in(cursor, connection, data, direction, truck, containers):
    # Check for existing recent transaction for this truck/direction
    existing_in_query = """
        SELECT t1.id, t1.session
        FROM transactions t1
        LEFT JOIN (
            SELECT truck, MAX(datetime) as latest_out_time
            FROM transactions
            WHERE truck = %s AND direction = 'out'
            GROUP BY truck
        ) t2 ON t1.truck = t2.truck
        WHERE t1.truck = %s AND t1.direction = 'in'
            AND (t2.latest_out_time IS NULL OR t1.datetime > t2.latest_out_time)
        ORDER BY t1.datetime DESC
        LIMIT 1
    """
    cursor.execute(existing_in_query, (truck, truck))
    existing_entry = cursor.fetchone()

    # Handle force flag for repeated transactions
    force = data.get('force', False)
    if existing_entry and not force:
        return jsonify({"error": "Transaction already exists. Use force=true to overwrite."}), 400

    # Prepare transaction data
    now = datetime.now()
    # we verified we have weight in data already
    weight = convert_to_kg(data.get('weight'), data.get('unit', 'lbs'))
    unit = 'kg'
    produce = data.get('produce', 'na')

    # set up the last session id to maintaine continues
    if existing_entry and force:
        # If overriding an existing entry, use its session ID
        session_id = existing_entry['session']
        # Delete the existing entry if force=true
        delete_query = "DELETE FROM transactions WHERE id = %s"
        cursor.execute(delete_query, (existing_entry['id'],))
    else:
        # Get a new session ID
        cursor.execute("SELECT MAX(session) as max_session FROM transactions")
        session_result = cursor.fetchone()
        if session_result is None or session_result['max_session'] is None:
            session_id = 1
        else:
            session_id = session_result['max_session'] + 1

    # Handle different scenarios
    # Insert truck transaction
    if truck != 'na':
        query = """
            INSERT INTO transactions
            (datetime, direction, truck, containers, bruto, produce, session)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (now, direction, truck,
                  json.dumps(containers.split(',')) if containers else None,
                  weight, produce, session_id)
        cursor.execute(query, values)
        transaction_id = cursor.lastrowid

    # Handle container registration logic for 'none' direction
    elif direction == 'none':
        if not containers:
            return jsonify({"error": "No containers specified for 'none' direction"}), 400

        containers_list = containers.split(',')
        if len(containers_list) > 1:
            return jsonify({"error": "Trying to weight more than 1 container"}), 400
        container_query = """
            INSERT INTO containers_registered
            (container_id, weight, unit)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE weight = %s, unit = %s
        """
        cursor.execute(container_query, (containers,
                        weight, unit, weight, unit))
        transaction_id = containers # name

    connection.commit()

    # Prepare response
    response = {
        "id": transaction_id,
        "truck": truck,
        "bruto": weight,
        "session": session_id
    }

    return jsonify(response), 201


def handle_weight_out(cursor, connection, data, truck):
    # Validate truck and containers
    if truck == 'na':
        return jsonify({"error": "Must specify either truck "}), 400

    # Find the most recent entry for this truck
    find_entry_query = """
    SELECT id, truck, bruto, session, containers, produce
    FROM transactions
    WHERE truck = %s AND direction = 'in'
    ORDER BY datetime DESC
    LIMIT 1
    """
    cursor.execute(find_entry_query, (truck,))
    entry_record = cursor.fetchone()
    
    # Validate entry record exists
    if not entry_record:
        return jsonify({"error": f"No entry record found for truck {truck}"}), 404
    containers = json.loads(entry_record['containers']) if entry_record.get('containers') else []

    # Validate entry record exists
    if truck != 'na' and not entry_record:
        return jsonify({"error": f"No entry record found for truck {truck}"}), 404

    # Calculate container weights
    total_container_tara = 0
    if containers:
        for container in containers:
            # Fetch container weight from registered containers
            container_query = "SELECT weight, unit FROM containers_registered WHERE container_id = %s"
            cursor.execute(container_query, (container,))
            container_record = cursor.fetchone()

            if not container_record:
                total_container_tara = None
                break
            weight = convert_to_kg(container_record.get('weight',0), container_record.get('unit', 'kg'))
            total_container_tara += weight

    # Prepare out transaction
    now = datetime.now()
    out_weight = convert_to_kg(data['weight'], data['unit'])

    # Calculate neto
    if truck != 'na':
        # Use current out_weight as truck tara
        truck_tara = out_weight

        # Use previous entry's bruto as the entry weight
        entry_bruto = entry_record['bruto']

        # Calculate neto
        neto = "na"
        if total_container_tara is not None:
            neto = entry_bruto - truck_tara - total_container_tara

        # Insert out transaction
        query = """
        INSERT INTO transactions
        (datetime, direction, truck, bruto,
         truckTara, neto, containers, produce, session)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            now,
            'out',
            truck,
            entry_bruto,
            truck_tara,  # truck tara from current out weight
            neto if neto != "na" else None,
            json.dumps(containers) if containers else None,
            # include produce, defaulting to 'na'
            entry_record.get('produce', 'na'),
            entry_record['session']
        )
        cursor.execute(query, values)
        transaction_id = cursor.lastrowid

        # Prepare response
        response = {
            "id": transaction_id,
            "truck": truck,
            "bruto": entry_bruto,
            "truckTara": truck_tara,
            "neto": neto
        }
    else:
        # Handle standalone container out transaction
        response = {
            "truck": "na",
            "bruto": out_weight
        }

    connection.commit()
    return jsonify(response), 201

    # If we get here, all retries failed
    print(f"All {max_retries} connection attempts failed. Last error: {last_error}")
    return None


def post_weight():
    print("sup", flush=True)
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Validate required fields
        required_fields = ['direction', 'weight', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Normalize inputs
        direction = data.get('direction', 'na').lower()
        truck = data.get('truck', 'na')
        containers = data.get('containers', None)

        # Validate direction
        valid_directions = ['in', 'out', 'none']
        if direction not in valid_directions:
            return jsonify({"error": "Invalid direction. Must be 'in', 'out', or 'none'"}), 400

        # Create database connection
        connection = mysqlweight.create_connection_with_retry()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        try:
            # Handle different scenarios based on direction
            if direction in ['in', 'none']:
                return handle_weight_in(cursor, connection, data, direction, truck, containers)
            elif direction == 'out':
                return handle_weight_out(cursor, connection, data, truck)

        except Exception as e:
            connection.rollback()
            print(f"Error processing transaction: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500
