from flask import request, jsonify, send_from_directory
from extensions.extensions import get_db_connection, socketio, app
import secrets
import string
import datetime

def generate_unique_ads_id(cur):
    while True:
        ads_id = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in 18)
        cur.execute("SELECT 1 FROM ads WHERE secret_id = %s", (ads_id,))
        if not cur.fetchone():
            return ads_id


def get_ads():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                    id AUTO_INCREMENT PRIMARY KEY,
                    ads_id VARCHAR(80) NOT NULL,
                    email VARCHAR(80) NOT NULL,
                    ad_title VARCHAR(250) NOT NULL,
                    ads_body VARCHAR(unlimited) NOT NULL,
                )
        """)
        conn.commit()

        email = request.form.get('email')
        if email:
            cur.execute("SELECT * FROM ads WHERE email = %s", (email,))
        else:
            cur.execute("SELECT * FROM ads")

        ads = cur.fetchall()
        cur.close()
        conn.close()

        if ads:
            return jsonify({'status': 200, 'ads': ads}), 200
        else:
            return jsonify({'status': 404, 'message': 'No ads found'}), 404

    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500
    
def add_ad():
    try:
        email = request.form.get('email')
        ad_title = request.form.get('ad_title')
        ads_body = request.form.get('ads_body')

        if not email or not ad_title or not ads_body:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        ads_id = generate_unique_ads_id(cur)

        cur.execute("""
            INSERT INTO ads (ads_id, email, ad_title, ads_body)
            VALUES (%s, %s, %s, %s)
        """, (ads_id, email, ad_title, ads_body))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'status': 200, 'ads_id': ads_id}), 200

    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500
    

def get_ad_by_id(ads_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM ads WHERE ads_id = %s", (ads_id,))
        ad = cur.fetchone()

        cur.close()
        conn.close()

        if ad:
            return jsonify({'status': 200, 'ad': ad}), 200
        else:
            return jsonify({'status': 404, 'message': 'Ad not found'}), 404

    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500
    
def ads_handler():
    if request.method == "POST":
        return get_ads()
    elif request.method == "GET":
        return add_ad()

def send_anonymous_message():
    email = request.form.get("email")
    receiver = request.form.get("receiver_email")
    message = request.form.get("message_content")
    message_id = request.form.get("message_id")
    
    # Capture only the hour and minute for the timestamp
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    if not email or not receiver or not message or not message_id:
        return jsonify({'message': 'Missing required fields', "status": 404}), 404
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create the messages table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message VARCHAR(250) NOT NULL,
                message_id VARCHAR(250) NOT NULL UNIQUE,
                email VARCHAR(80) NOT NULL,
                receiver VARCHAR(80) NOT NULL,
                timestamp VARCHAR(80) NOT NULL
            )
        """)
        
        # Insert the new message into the database
        cur.execute("""
            INSERT INTO messages (message, message_id, email, receiver, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (message, message_id, email, receiver, timestamp))
        
        conn.commit()
        cur.close()
        conn.close()

        socketio.emit("new_message", {
            "message": message,
            "email": email,
            "receiver": receiver
        })
        return jsonify({'message_id': message_id, "status": 200}), 200

    except Exception as e:
        return jsonify({'message': str(e), "status": 500}), 500
    

def send_ads_reply():
    ads_id = request.form.get("ads_id")
    email = request.form.get("email")
    reply = request.form.get("reply")
    receiver = request.form.get("receiver_email")
    
    if not ads_id or not email or not reply or not receiver:
        return jsonify({'message': 'Missing required fields', "status": 404}), 404
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ads_reply (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(80) NOT NULL,
            ads_id VARCHAR(250) NOT NULL,
            reply VARCHAR(250) NOT NULL,
            receiver VARCHAR(80) NOT NULL,
            accepted BOOL NOT NULL DEFAULT FALSE
        )
        """)
        
        cur.execute("""
            INSERT INTO ads_reply (email, ads_id, reply, receiver)
            VALUES (%s, %s, %s, %s)
        """, (email, ads_id, reply, receiver))
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Reply sent successfully', "status": 200}), 200

    except Exception as e:
        return jsonify({'message': str(e), "status": 500}), 500
    
def get_ads_reply():
    try:
        conn = get_db_connection()
        email = request.form.get("email")
        receiver = request.form.get("receiver")
        cur = conn.cursor()
        
        # Fetch all ads replies with accepted = False
        cur.execute("""
            SELECT ads_id, email, reply, receiver 
            FROM ads_reply 
            WHERE accepted = FALSE
            AND WHERE email = %s AND receiver = %s
        """, (email, receiver))
        replies = cur.fetchall()
        
        cur.close()
        conn.close()

        # Prepare the list of ads replies
        replies_list = [
            {
                'ads_id': reply[0],
                'email': reply[1],
                'reply': reply[2],
                'receiver': reply[3]
            }
            for reply in replies
        ]

        # Emit the list of ads replies using socketio
        socketio.emit('ads_replies_list', {'replies': replies_list})

        return jsonify({'message': 'Ads replies retrieved successfully'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

