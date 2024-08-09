from flask import request, jsonify
from extensions.extensions import get_db_connection, app, socketio
from functions.add_to_balance import add_to_balance


def updateBalance(amount, email, username):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT * FROM users WHERE username = %s AND email = %s
        """, (username, email))
        c = cur.fetchone()

        if c is not None:
            # User found, update balance
            socketio.emit("status", {"status": 200, "message": "User found. Updating balance."})
            return add_to_balance(username=username, email=email, amount=amount)
        else:
            # User not found
            socketio.emit("status", {"status": 404, "message": "No user found"})
            return jsonify({"message": "No such user found", "status": 404}), 404

    except Exception as e:
        print(e)
        return jsonify({"message": "Error updating balance"}), 500
    finally:
        cur.close()
        conn.close()