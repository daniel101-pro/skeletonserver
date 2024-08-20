from extensions.extensions import get_db_connection, app, socketio
from flask import request, jsonify, send_from_directory


def getschemas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS otp (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, otp TEXT
    """)
    conn.commit()
    cur.close()
    conn.close()