from extensions.extensions import get_db_connection, app, socketio
from flask import request, jsonify
import bcrypt
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

def signup():
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username") or email.split("@")[0]

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor()

        # Insert into users table
        cur.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """, (username, email, hashed_password))

        # Insert into balance table
        cur.execute("""
            INSERT INTO balance (username, email, balance)
            VALUES (%s, %s, %s)
        """, (username, email, 0.00))

        payload = {
            'username': username,
            'email': email,
            'balance': 0
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User registered successfully!", "status": 200, "token": token})

    except Exception as e:
        print(e)
        return jsonify({"message": "Error registering user"})


def login():
    try:
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT username, password FROM users WHERE email = %s
        """, (email,))
        user = cur.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            payload = {
                'username': user[0],
                'email': email
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            return jsonify({"message": "Login successful!", "status": 200, "token": token})
        else:
            return jsonify({"message": "Invalid email or password", "status": 404})

    except Exception as e:
        print(e)
        return jsonify({"message": "Error logging in"}), 500

