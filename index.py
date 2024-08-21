#
# ---- Beginning of Import Statements
#
from extensions.extensions import get_db_connection, app, socketio
from flask import request, jsonify
from flask_socketio import emit
from routes.auth import signup, login, check_email, get_balance, add_to_balance
from routes.balance import updateBalance
from routes.ads import ads_handler, send_anonymous_message, send_ads_reply, get_ads_reply, get_replies_to_ad, get_replies_from_ads
from routes.secrets import secret_handler, secrets_comments_handlers, search_secrets
from functions.share_to_media import shared_to_media
from schemas.get_schemas import getschemas
#
# ---- End of Import Statements
#





#
#
# ---- App Routes For Various Purposes (Beginning)
#
#


@app.route("/signup", methods=["POST"])
def register_user():
    return signup()

@app.route("/login", methods=["POST"])
def signin_user():
    return login()

@app.route("/verify", methods=["GET", "POST"])
def ver():
    return check_email()

@app.route("/secrets", methods=["GET", "POST"])
def secrets():
    return secret_handler()

@app.route("/get_replies_to_ads", methods=["GET", "POST"])
def get_ads_replies():
    return get_replies_to_ad()

@app.route("/get_replies_from_ads", methods=["GET", "POST"])
def get_adss_from_replies():
    return get_ads_reply()

@app.route("/addBalance", methods=["GET", "POST"])
def addBalance():
    return add_to_balance()

@app.route("/ads", methods=["GET", "POST"])
def ads():
    return ads_handler()

@app.route("/secret_comments", methods=["GET", "POST"])
def secret_comments():
    return secrets_comments_handlers()

@app.route("/search_secrets", methods=["GET", "POST"])
def search():
    return search_secrets()

@app.route("/fetch_balance", methods=["GET", "POST"])
def fetch_balance():
    return get_balance()

@app.route("/getdetails", methods=["GET", "POST"])
def getdetails():
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if 'balance' table exists
    cur.execute("SHOW TABLES LIKE 'balance'")
    balance_exists = cur.fetchone() is not None

    # Check if 'tasks' table exists
    cur.execute("SHOW TABLES LIKE 'tasks'")
    tasks_exists = cur.fetchone() is not None

    cur.close()
    conn.close()

    if balance_exists and tasks_exists:
        return jsonify({"status": "true"}), 200
    elif balance_exists or tasks_exists:
        return jsonify({"status": "half"}), 200
    else:
        return jsonify({"status": "false"}), 200

@app.route("/send_ads_replyy", methods=["GET", "POST"])
def ads_reply_type():
    return send_ads_reply()

#
#
# ---- App Routes For Various Purposes (Ending)
#
#








#
#
# ---- Web Socket Handlers (Beginning)
#
#


@socketio.on("connect")
def connect():
    print("Client connected successfully through sockets")
    emit("message", {"data": "Connected to the server"})

@socketio.on("send_anonymous_message")
def send_anonymous_message():
    print("Sending Message")
    return send_anonymous_message()

@socketio.on("get_ads_reply")
def ads_reply():
    print("WWW")
    return get_ads_reply()

@socketio.on("send_ads_reply")
def send_ads_reply2():
    print("Idk just felt like printing shii")
    return send_ads_reply() 

@socketio.on("disconnect")
def disconnect():
    print("Client disconnected from server")

@socketio.on("update_balance")
def handle_update_balance(data):
    amount = data.get("amount")
    email = data.get("email")
    username = data.get("username")
    updateBalance(amount, email, username)

@socketio.on("share_count")
def share():
    data = request.json
    count = data.get("count")
    email = data.get("email")
    username = data.get("username")
    return shared_to_media(count=count, email=email, username=username)


#
#
# ---- Web Socket Handlers (Ending)
#
#





#
#
# ---- Running the script and setting up database schemas (Beginning)...
#
#


if __name__ == "__main__":
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS otp (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            otp TEXT NOT NULL,
            email TEXT NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()  # Make sure to commit changes
    cur.close()
    conn.close()   # Close the connection when done
    socketio.run(app, host="0.0.0.0", port=1234, use_reloader=True, debug=True)

#
#
# ---- Running the script and setting up database schemas (Ending)...
#
#