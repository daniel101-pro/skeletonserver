from extensions.extensions import get_db_connection, app, socketio, mail, Message
from flask import request, jsonify
import bcrypt
import jwt
import random
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

def check_email():
    try:
        email = request.form.get("email")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM users WHERE email = %s
        """, (email,))
        user = cur.fetchone()
        if user is None:
            return sendOTP(email=email)
        return jsonify({'status': 404})
    except Exception as e:
        return jsonify({'status': 500, "error": str(e)})


def sendOTP(email):
    try:
        # Generate a random 6-digit OTP
        otp = ''.join(random.choices('0123456789', k=4))

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert OTP into the database
        cursor.execute('INSERT INTO otp (email, otp) VALUES (%s, %s)', (email, otp))
        conn.commit()
        conn.close()

        # Send the OTP via email
        msg = Message('Skeleton Dating Service', sender='falodun379@gmail.com', recipients=[email])
        msg_body = f"\n Your One-Time Password is {otp} \n\n\n\n Make sure to not share this code with anyone"
        msg.body = msg_body
        mail.send(msg)

        return jsonify({"status": 200, "success": "OTP sent successfully", "otp": otp})

    except Exception as e:
        return jsonify({"status": 500, "error": str(e)})

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

def get_balance():
    try:
        email = request.form.get("email")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE email = %s", (email,))
        balance = cur.fetchone()

        if balance is not None:
            return jsonify({ 'status': 200, 'balance': balance}), 200
        return jsonify({'status': 404, 'balance': 'He, You wish', "message": 'No such user with email'}), 404
    except Exception as e:
        return jsonify({'status': 500, "exception": str(e), "message": 'Network or some tiring shii'}), 500

def add_to_balance():
    try:
        # Get email and amount from the request
        email = request.form.get("email")
        amount = float(request.form.get("amount"))  # Ensure amount is treated as a float
        
        # Check if both email and amount are provided
        if not email or amount is None:
            return jsonify({'status': 'error', 'message': 'Email and amount are required'}), 400

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Execute the update query
        cur.execute("""
            UPDATE users
            SET balance = balance + %s
            WHERE email = %s
        """, (amount, email))
        
        # Commit the transaction
        conn.commit()
        
        # Check if any rows were updated
        if cur.rowcount == 0:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Balance updated successfully'}), 200

    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        
        # Close the cursor and connection if they were created
        if cur:
            cur.close()
        if conn:
            conn.close()
        
        # Return an error response
        return jsonify({'status': 'error', 'message': str(e)}), 500

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

