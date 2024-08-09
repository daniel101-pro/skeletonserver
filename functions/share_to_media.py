from flask import request, jsonify, send_from_directory
from extensions.extensions import app, socketio, get_db_connection
from constants.text import text

def shared_to_media(count, email, username):
    try:
        if count < 20:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE tasks
                SET task_share_count = %s
                WHERE username = %s 
                AND email = %s
            """, (count, username, email))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"message": "Task share count updated successfully", "status": 200}), 200
        else:
            return jsonify({"message": "Share count limit reached", "status": 400}), 400
    except Exception as e:
        print(e)
        return jsonify({"message": "Error updating task share count", "status": 500}), 500
