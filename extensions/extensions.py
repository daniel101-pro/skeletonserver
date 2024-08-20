from dotenv import load_dotenv
import os
import pymysql
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Mail configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "falodun379@gmail.com"
app.config["MAIL_PASSWORD"] = "oecz qyew jrim boxy"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True


socketio = SocketIO(app)
db = SQLAlchemy(app)
mail = Mail(app)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins



def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
        ssl={'ssl': {'ssl-mode': os.getenv('DB_SSL_MODE')}}
    )
    return connection