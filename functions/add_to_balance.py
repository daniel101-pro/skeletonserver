from extensions.extensions import app, socketio, get_db_connection
from flask import request, jsonify

def add_to_balance(username, email, amount):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update the balance for the specified user
        cur.execute("""
            UPDATE balance 
            SET balance = balance + %s 
            WHERE email = %s AND username = %s
        """, (amount, email, username))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Balance updated successfully!", "status": 200}), 200

    except Exception as e:
        print(e)
        return jsonify({"message": "Error updating balance", "status": 500}), 500
