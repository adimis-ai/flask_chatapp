from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_socketio import join_room
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import json_util
from friend_rec_sys import suggested_friends

# SECTION: Flask App, MongoDB Atlas, and SocketIO Initialization
app = Flask(__name__)
app.secret_key = "sfdjkafnk"
socketio = SocketIO(app)
scheduler = BackgroundScheduler()
bcrypt = Bcrypt()

# SECTION: MongoDB Configuration
client = MongoClient("mongodb+srv://adimis:root@alicememory.49huuqd.mongodb.net/?retryWrites=true&w=majority")

chat_db = client.get_database("ChatDB-15")
users_collection = chat_db.get_collection("users")
chat_messages_collection = chat_db.get_collection("chat_messages")

# SECTION: JWT Manager Initialization
jwt = JWTManager(app)

# SECTION: Online/Offline Check
def check_online_status():
    current_time = datetime.now()
    users = users_collection.find()

    for user in users:
        last_activity = user.get('last_activity')
        if last_activity:
            time_difference = current_time - last_activity
            if time_difference <= timedelta(minutes=5):
                users_collection.update_one({"_id": user["_id"]}, {"$set": {"online": True}})
            else:
                users_collection.update_one({"_id": user["_id"]}, {"$set": {"online": False}})

scheduler.add_job(check_online_status, 'interval', minutes=5)
scheduler.start()

# SECTION: Models
class User:
    def __init__(self, username, age, email, password):
        self.username = username
        self.age = age
        self.email = email
        self.password = password
        self.online = False
        self.last_activity = None
        self.friends = []

    def to_dict(self):
        # Convert the User object to a dictionary
        return {
            "username": self.username,
            "age": self.age,
            "email": self.email,
            "password": self.password,
            "online": self.online,
            "last_activity": self.last_activity,
            "friends": self.friends,
        }

class Message:
    def __init__(self, sender_username, receiver_username, content):
        self.sender_username = sender_username
        self.receiver_username = receiver_username
        self.content = content
        self.timestamp = datetime.now()

    def to_dict(self):
        # Convert the Message object to a dictionary
        return {
            "sender_username": self.sender_username,
            "receiver_username": self.receiver_username,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }

class ChatHistory:
    def __init__(self, sender_username, receiver_username, messages=[]):
        self.sender_username = sender_username
        self.receiver_username = receiver_username
        self.messages = messages

    def to_dict(self):
        # Convert the ChatHistory object to a dictionary
        return {
            "sender_username": self.sender,
            "receiver_username": self.receiver,
            "messages": self.messages
        }
    
# SECTION: Database Class
class Database:
    @staticmethod
    def create_user(user):
        try:
            users_collection.insert_one(user)
            return True
        except DuplicateKeyError:
            return False

    @staticmethod
    def get_user_by_id(user_id):
        return users_collection.find_one({"_id": user_id})

    @staticmethod
    def get_user_by_username(username):
        user = users_collection.find_one({"username": username})
        return user

    @staticmethod
    def save_chat_message(sender_username, receiver_username, message_content):
        try:
            print(f"Saving message from {sender_username} to {receiver_username}: {message_content}")

            message = Message(sender_username=sender_username, receiver_username=receiver_username, content=message_content)
            chat_messages_collection.insert_one(message.to_dict())  # Insert the message into the chat_messages collection

            print("Message saved successfully.")
        except PyMongoError as e:
            print(f"Error saving message: {str(e)}")

    @staticmethod
    def get_chat_history(sender_username, receiver_username):
        try:
            # Query the chat_messages collection to retrieve chat history
            chat_history = chat_messages_collection.find({
                "$or": [
                    {"sender_username": sender_username, "receiver_username": receiver_username},
                    {"sender_username": receiver_username, "receiver_username": sender_username}
                ]
            })

            # Convert the chat history to a list of message dictionaries
            chat_history_list = [json_util.dumps(message, default=json_util.default) for message in chat_history]

            print("Chat history retrieved successfully.")
            return chat_history_list
        except PyMongoError as e:
            print(f"Error retrieving chat history: {str(e)}")

    @staticmethod
    def get_user_by_email(email):
        return users_collection.find_one({"email": email})

db = Database()

# SECTION: Routes
@app.route('/api/register/', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    age = data['age']
    interests = data.get('interests', {})

    print(f"Registering user: username={username}, email={email}")

    # Check if a user with the same email or username already exists
    existing_user_by_email = db.get_user_by_email(email)
    existing_user_by_username = db.get_user_by_username(username)

    if existing_user_by_email:
        return jsonify({"error": "Email already exists. Please use a different email."}), 400
    elif existing_user_by_username:
        return jsonify({"error": "Username already exists. Please choose a different username."}), 400

    # If no user with the same email or username exists, create a new user
    new_user = User(username, age, email, password)
    new_user.interests = interests

    # Set online status and last_activity
    new_user.online = True
    new_user.last_activity = datetime.now()

    if db.create_user(new_user.to_dict()):
        print("User registered successfully")
        return jsonify({"message": "User registered successfully"}), 200
    else:
        print("Username or email already exists")
        return jsonify({"error": "Registration failed. Please try again later."}), 500

@app.route('/api/login/', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    print(f"Logging in user: username={username}")

    user = db.get_user_by_username(username)

    if user and bcrypt.check_password_hash(user['password'], password):
        print("Login successful")

        # Set online status and last_activity
        users_collection.update_one({"username": username}, {"$set": {"online": True, "last_activity": datetime.now()}})

        access_token = create_access_token(identity=username)
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    else:
        print("Invalid credentials")
        return jsonify({"error": "Invalid username or password. Please try again."}), 401

@app.route('/api/online-users/')
@jwt_required()
def get_online_users():
    online_users = users_collection.find({"online": True}, {"_id": 0, "password": 0})
    online_user_list = list(online_users)
    return jsonify({"online_users": online_user_list}), 200

@app.route('/api/get_chat_history/', methods=['POST'])
@jwt_required()
def get_user_chat_history():
    try:
        data = request.json
        sender_username = get_jwt_identity()
        receiver_username = data.get('receiver')

        if not receiver_username:
            return jsonify({"message": "Receiver username is required"}), 400

        print(f"Retrieving chat history for sender {sender_username} and receiver {receiver_username}")

        # Retrieve the chat history for the sender and receiver
        chat_history = db.get_chat_history(sender_username, receiver_username)

        print("Chat history retrieved successfully.", chat_history)

        return jsonify({"chat_history": chat_history}), 200
    except PyMongoError as e:
        print(f"Error in get_user_chat_history: {str(e)}")
        return jsonify({"message": "An error occurred while retrieving chat history"}), 500
    except Exception as e:
        print(f"Unexpected error in get_user_chat_history: {str(e)}")
        return jsonify({"message": "An unexpected error occurred"}), 500

# Endpoint to get friend recommendations with explanations
@app.route('/api/suggested-friends/<user_id>', methods=['GET'])
def friend_recommendation_system(user_id):
    recommendations = suggested_friends(user_id)
    return recommendations

@socketio.on('start_chat')
def handle_start_chat_event(data):
    sender_username = data["username"]
    receiver_username = data["receiver"]

    # Check if the receiver is online and available, and then join the chat room
    receiver = db.get_user_by_username(receiver_username)
    if receiver and receiver['online']:
        chat_room = f"{sender_username}_{receiver_username}"
        join_room(chat_room)
        emit('chat_started', {"message": "Chat started successfully", "chat_room": chat_room})
    else:
        emit('chat_error', {"message": "Receiver is offline"}, room=request.sid)

@socketio.on('send_message')
def handle_send_message_event(data):
    sender_username = data["username"]
    receiver_username = data["receiver"]
    message_content = data["message"]

    # Find the sender and receiver users in the database
    sender = db.get_user_by_username(sender_username)
    receiver = db.get_user_by_username(receiver_username)

    if sender and receiver:
        app.logger.info("Sender and receiver found in the database")

        if receiver['online']:
            # Create a Message object and add it to the chat
            message = Message(sender_username=sender_username, receiver_username=receiver_username, content=message_content)

            app.logger.info("Message from {} to {}: {}".format(sender['username'], receiver['username'], message.to_dict()))

            # Emit the message to the sender and receiver in their chat room
            chat_room = f"{sender['username']}_{receiver['username']}"
            message_data = {
                'sender': sender['username'],  # Include the sender's username
                'receiver': receiver['username'],
                'content': message.to_dict()  # Include the message content
            }

            db.save_chat_message(sender_username, receiver_username, message_content)

            app.logger.info("Message emitted in chat room {}: {}".format(chat_room, message.to_dict()))
            emit('receive_message', message_data, room=chat_room)

            app.logger.info("Message sent and chat history updated")

        else:
            app.logger.error("Receiver is offline")
            chat_room = f"{sender['username']}_{receiver['username']}"
            emit('error_message', {"message": "Receiver is offline"}, room=chat_room)

        # Check if sender is offline and update their online status and last_activity
        if not sender['online']:
            users_collection.update_one({"username": sender_username}, {"$set": {"online": True, "last_activity": datetime.now()}})
    else:
        app.logger.error("Sender or receiver not found")

if __name__ == '__main__':
    socketio.run(app, debug=True)
