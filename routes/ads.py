from flask import request, jsonify, send_from_directory
from extensions.extensions import get_db_connection, socketio, app
import secrets
from constructs.haversine import haversine
import string
import datetime

def generate_unique_ads_id(cur):
    while True:
        # Generate a unique ID of length 18
        ads_id = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(18))
        
        # Check if the generated ID already exists in the database
        cur.execute("SELECT 1 FROM ads WHERE ads_id = %s", (ads_id,))
        if not cur.fetchone():
            return ads_id
        
def get_replies_from_ads():
    try:
        email = request.form.get("email")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS request_replies (
                id SERIAL PRIMARY KEY,
                ads_id INTEGER NOT NULL,
                email_ads VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                reply TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

        """)
        cur.execute("""
            SELECT ads_id, email_ads, email, reply FROM request_replies WHERE email = %s
        """, (email,))
        request_replies = cur.fetchall()

        if request_replies is not None:
            return jsonify({'message': "fetched succesfuly", "status": 200, 'request_replies': request_replies})
        else:
            return jsonify({"message": "Error In fetching", "status": 404}), 404
    except Exception as e:
        return jsonify({"messge": 'Network Error', "status": 500, 'exception': str(e)}), 500    


def get_replies_to_ad():
    try:
        email_a = request.form.get("email")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS request_replies (
                id SERIAL PRIMARY KEY,
                ads_id INTEGER NOT NULL,
                email_ads VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                reply TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

        """)
        cur.execute("""
            SELECT ads_id, email_ads, reply FROM request_replies WHERE email_ads = %s
        """, (email_a,))
        request_replies = cur.fetchall()
        
        if request_replies is not None:
            return jsonify({"message": 'Fetched successfully', 'status': 200, 'request_replies': request_replies}), 200
        else:
            return jsonify({"message": "Error In fetching", "status": 404}), 404
    except Exception as e:
        return jsonify({"messge": 'Network Error', "status": 500, 'exception': str(e)}), 500    


def reply_ad():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Create the table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS request_replies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ads_id VARCHAR(80) NOT NULL,
                email_ads VARCHAR(80) NOT NULL,
                email VARCHAR(80) NOT NULL,
                reply TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert a new reply
        ads_id = request.form.get('ads_id')
        email = request.form.get('email')
        reply = request.form.get('reply')

        cur.execute("""
            INSERT INTO request_replies (ads_id, email, reply)
            VALUES (%s, %s, %s)
        """, (ads_id, email, reply))

        conn.commit()
        return jsonify({'status': 200, 'message': 'Reply added successfully'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        cur.close()
        conn.close()



def get_ads():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the columns already exist before trying to add them
        cur.execute("SHOW COLUMNS FROM ads LIKE 'city'")
        result = cur.fetchone()
        if not result:
            cur.execute("ALTER TABLE ads ADD COLUMN city VARCHAR(100)")
        
        cur.execute("SHOW COLUMNS FROM ads LIKE 'state'")
        result = cur.fetchone()
        if not result:
            cur.execute("ALTER TABLE ads ADD COLUMN state VARCHAR(100)")

        cur.execute("SHOW COLUMNS FROM ads LIKE 'country'")
        result = cur.fetchone()
        if not result:
            cur.execute("ALTER TABLE ads ADD COLUMN country VARCHAR(100)")

        cur.execute("SHOW COLUMNS FROM ads LIKE 'reviewed'")
        result = cur.fetchone()
        if not result:
            cur.execute("ALTER TABLE ads ADD COLUMN reviewed BOOL DEFAULT false")
            

        # Create the ads table if it doesn't exist
        cur.execute("""
           CREATE TABLE IF NOT EXISTS ads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ads_id VARCHAR(80) NOT NULL,
                email VARCHAR(80) NOT NULL,
                ad_title VARCHAR(250) NOT NULL,
                ads_body VARCHAR(250) NOT NULL,
                city VARCHAR(100),
                state VARCHAR(100),
                country VARCHAR(100),
                reviewed BOOL DEFAULT false
            )
        """)
        conn.commit()

        email = request.form.get('email')
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
        ads_body = request.form.get('ads_body')
        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get('country')

        if not email or not city or not state or not country or not ads_body:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        ads_id = generate_unique_ads_id(cur)
        amount = 10

        # Update user balance
        cur.execute("""
            UPDATE users
            SET balance = balance - %s
            WHERE email = %s
        """, (amount, email))

        # Insert new ad
        cur.execute("""
            INSERT INTO ads (ads_id, email, ad_title, ads_body, city, state, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (ads_id, email, ads_body, ads_body, city, state, country))

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
        return add_ad()
    elif request.method == "GET":
        return get_ads()

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
        print(f"eeee: {receiver}")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ads_reply (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(80) NOT NULL,
            ads_id VARCHAR(250) NOT NULL,
            reply VARCHAR(250) NOT NULL,
            gender VARCHAR(80) NOT NULL DEFAULT 'male',
            receiver VARCHAR(80) NOT NULL,
            accepted BOOL NOT NULL DEFAULT FALSE
        )
        """)

        try:
            cur.execute("""
                ALTER TABLE ads_reply
                    ALTER COLUMN gender SET DEFAULT 'male';
            """)
        except Exception as e:
            print(f"Error with exception: {e}")
        
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
        print(f"receiver: {str(receiver)}")
        receiver = str(receiver.strip()) if receiver else None
        print(f"receiver after strip: {receiver}")

        cur.execute("""
            SELECT ads_id, email, reply, receiver 
            FROM ads_reply WHERE email = %s
            
        """, (receiver,))
        replies = cur.fetchall()
        print(f"REceiver: {replies}")
        
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
        print(f"repliesList: {replies_list}")

        # Emit the list of ads replies using socketio
        socketio.emit('ads_replies_list', {'replies': replies_list})

        return jsonify({'message': 'Ads replies retrieved successfully', 'replies': replies_list, 'status': 200}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


def filter_ads_by_location():
    try:
        # Get the location of the receiver
        longitude_receiver = float(request.form.get("longitude"))
        latitude_receiver = float(request.form.get("latitude"))
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Retrieve all ads
        cur.execute("SELECT ads_id, email, ad_title, longitude, latitude, ads_body FROM ads")
        ads = cur.fetchall()
        
        filtered_ads = []

        # Define a function to check if two coordinates are in the same state
        def is_same_state(lat1, lon1, lat2, lon2):
            # Haversine function to calculate distance between two points
            distance = haversine(lat1, lon1, lat2, lon2)
            # Assume that within 100 km, it's the same state (adjust as needed)
            return distance <= 100

        # Filter ads based on location
        for ad in ads:
            ad_id, email, ad_title, lon, lat, ads_body = ad
            if is_same_state(latitude_receiver, longitude_receiver, float(lat), float(lon)):
                filtered_ads.append({
                    'ads_id': ad_id,
                    'email': email,
                    'ad_title': ad_title,
                    'longitude': lon,
                    'latitude': lat,
                    'ads_body': ads_body
                })

        cur.close()
        conn.close()

        # Check if any ads were found in the same state
        if filtered_ads:
            return jsonify({'status': 200, 'ads': filtered_ads}), 200
        else:
            return jsonify({'status': 404, 'message': 'No ads found in the same state'}), 404

    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500
    
