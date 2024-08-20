from flask import jsonify, request
from extensions.extensions import app, socketio, get_db_connection
import secrets
import string

def generate_unique_secret_id(cur):
    while True:
        secret_id = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(18))
        cur.execute("SELECT 1 FROM secrets WHERE secret_id = %s", (secret_id,))
        if not cur.fetchone():
            return secret_id


def add_a_secret():
    try:
        email = request.form.get("email")
        secret = request.form.get("secret_body")
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS secrets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                secret_id VARCHAR(256) UNIQUE NOT NULL,
                secret_body VARCHAR(256) NOT NULL,
                email VARCHAR(80) NOT NULL,
                likes TEXT
            )
        """)


        secret_id = generate_unique_secret_id(cur)
        
        cur.execute("""
            INSERT INTO secrets (secret_id, secret_body, email)
            VALUES (%s, %s, %s)
        """, (secret_id, secret, email))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Secret added successfully!", "secret_id": secret_id, "status": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        



def get_secrets():
    try:
        email = request.form.get("email")
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS secrets (
                id INT PRIMARY KEY AUTO_INCREMENT,
                secret_id VARCHAR(256) UNIQUE NOT NULL,
                secret_body VARCHAR(256) NOT NULL,
                email VARCHAR(80) NOT NULL,
                likes JSON
            )
        """)

        cur.execute("""
            SELECT secret_id, secret_body, email, likes 
            FROM secrets 
            ORDER BY id ASC 
            LIMIT 10
        """)
        secrets = cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
        if secrets is not None:

            secrets_list = []
            for secret in secrets:
                secrets_list.append({
                    "secret_id": secret[0],
                    "secret_body": secret[1],
                    "email": secret[2],
                    "likes": secret[3]
                })

            return jsonify({"secrets": secrets_list, "status": 200}), 200
        else:
            return jsonify({"status": 404, "message": 'secresttypeshii'}), 404
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500

def secret_handler():
    if request.method == "POST":
        return add_a_secret()
    elif request.method == "GET":
        return get_secrets()


def add_secret_comment():
    try:
        secret_id = request.form.get("secret_id")
        comment = request.form.get("comment")
        email = request.form.get("email")
        conn = get_db_connection()
        cur = conn.cursor()

        # Create the `secret_comments` table if it doesn't already exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS secret_comments (
                id INT PRIMARY KEY AUTO_INCREMENT,
                secret_id VARCHAR(256) NOT NULL,
                email VARCHAR(80) NOT NULL,
                comment VARCHAR(250) NOT NULL,
                likes JSON DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert the new comment into the `secret_comments` table
        cur.execute("""
            INSERT INTO secret_comments (secret_id, email, comment)
            VALUES (%s, %s, %s)
        """, (secret_id, email, comment))
        
        conn.commit()
        cur.close()
        conn.close()
        # Emit the comment and email to update the comment section in real-time
        socketio.emit("update_comment_section", {
            "comment": comment,
            "email": email
        })
        return jsonify({"message": "Comment added successfully!", "status": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500
        

def search_secrets():
    try:
        query = request.form.get("query")
        conn = get_db_connection()
        cur = conn.cursor()
        
        search_query = f"%{query}%"
        cur.execute("""
            SELECT secret_id, secret_body, email, likes 
            FROM secrets 
            WHERE email LIKE %s OR secret_body LIKE %s
        """, (search_query, search_query))
        
        secrets = cur.fetchall()

        secrets_list = []
        for secret in secrets:
            secrets_list.append({
                "secret_id": secret[0],
                "secret_body": secret[1],
                "email": secret[2],
                "likes": secret[3]
            })
        socketio.emit("update_secrets_feed", {
            "secrets": secrets_list,
            "query": search_query
        })
        return jsonify({"secrets": secrets_list, "status": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500
    finally:
        cur.close()
        conn.close()

def get_secret_comments():
    try:
        # Retrieve the 'email' and 'secret_id' from the query parameters
        email = request.args.get("email")
        secret_id = request.args.get("secret_id")

        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch comments related to the specific secret_id
        cur.execute("""
            SELECT comment, email, likes, created_at 
            FROM secret_comments 
            WHERE secret_id = %s
            ORDER BY created_at ASC
        """, (secret_id,))

        comments = cur.fetchall()

        # Format the results into a list of dictionaries
        comments_list = []
        for comment in comments:
            comments_list.append({
                "comment": comment[0],
                "email": comment[1],
                "likes": comment[2],
                "created_at": comment[3]
            })

        return jsonify({"comments": comments_list, "status": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500
    finally:
        cur.close()
        conn.close()


def secrets_comments_handlers():
    if request.method == "POST":
        return add_secret_comment()
    elif request.method == "GET":
        return get_secret_comments()