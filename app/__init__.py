# app/__init__.py
from flask import Flask
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import JWTManager
from flask_pymongo import MongoClient
from flask_bcrypt import Bcrypt
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
scheduler = BackgroundScheduler()
bcrypt = Bcrypt()
jwt = JWTManager(app)

client = MongoClient(app.config['MONGODB_ATLAS_URI'])
chat_db = client.get_database(app.config['DATABASE_NAME'])
users_collection = chat_db.get_collection(app.config['USERS_COLLECTION'])
chat_messages_collection = chat_db.get_collection(app.config['CHAT_MESSAGES_COLLECTION'])

from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.friend_recommendation import friend_rec_bp
from app.socket_events.chat_events import *

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(friend_rec_bp)
