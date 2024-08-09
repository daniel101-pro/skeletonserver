#
# ---- Beginning of Import Statements
#
from extensions.extensions import get_db_connection, app, socketio
from flask import request, jsonify
from flask_socketio import emit
from routes.auth import signup, login
from routes.balance import updateBalance
from routes.ads import ads_handler
from routes.secrets import secret_handler, secrets_comments_handlers, search_secrets
from functions.share_to_media import shared_to_media
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

@app.route("/secrets", methods=["GET", "POST"])
def secrets():
    return secret_handler()

@app.route("/ads", methods=["GET", "POST"])
def ads():
    return ads_handler()

@app.route("/secret_comments", methods=["GET", "POST"])
def secret_comments():
    return secrets_comments_handlers()

@app.route("/search_secrets", methods=["GET", "POST"])
def search():
    return search_secrets()

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
    socketio.run(app, host="0.0.0.0", port=1234, use_reloader=True, debug=True)


#
#
# ---- Running the script and setting up database schemas (Ending)...
#
#