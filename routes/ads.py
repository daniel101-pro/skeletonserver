from flask import request, jsonify, send_from_directory
from extensions.extensions import get_db_connection, socketio, app
import secrets
import string

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