Create a professional and well documented documentation for this Chatapp prototype I created using Flask, socket.io and mongodb atlas.

# /home/adimis/Desktop/chatapp/tests/automated_test.py:
```py
import requests
import json
import socketio
from colorama import init, Fore, Style
from datetime import datetime

# Configuration
class Config:
    BASE_URL = "http://localhost:5000"  # Replace with the actual URL
    USER1_USERNAME = "user1"
    USER1_PASSWORD = "password1"
    USER2_USERNAME = "user2"
    USER2_PASSWORD = "password2"

# Initialize the socket.io client
sio = socketio.Client()

# Helper functions for API requests
def api_post(endpoint, data=None, headers=None):
    url = f"{Config.BASE_URL}/{endpoint}"
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request Error: {e}")
        return None

# Function to test friend recommendation system
def get_suggested_friends(user_id):
    # Send a GET request to the server to get suggested friends for the user with the given user_id
    response = requests.get(f'{Config.BASE_URL}/api/suggested-friends/{user_id}')

    # Check the response status code
    if response.status_code == 200:
        # If the status code is 200 (OK), parse the JSON response
        data = response.json()

        # Check if the response contains the 'recommended_friends' key
        if 'recommended_friends' in data:
            recommended_friends = data['recommended_friends']
            return recommended_friends
        else:
            raise ValueError('Response does not contain recommended_friends')
    elif response.status_code == 404:
        raise ValueError(f'User with ID {user_id} not found')
    else:
        raise ValueError(f'Request failed with status code {response.status_code}')

# Function to register a new user
def register_user(username, password):
    email = f"{username}@gmail.com"
    data = {
        "username": username,
        "age": 25,
        "email": email,
        "password": password,
        "interests": {},
    }
    
    response = api_post("/api/register/", data)
    
    if response:
        print(f"User {username} registered successfully")
    else:
        print(f"Failed to register user {username}")

# User login
def login_user(username, password):
    data = {
        "username": username,
        "password": password,
    }
    
    response = api_post("api/login", data)
    
    if response:
        token = response.json().get("access_token")
        print(f"User: {username} logged in successfully")
        return token
    else:
        print(f"Failed to log in user {username}")

# Function to get a list of online users
def get_online_users(token):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(f"{Config.BASE_URL}/api/online-users/", headers=headers)
    return response.json()

# Send a message using socket.io
def send_message(username, receiver_username, message):
    data = {
        "username": username,
        "receiver": receiver_username,
        "message": message,
    }
    sio.emit("send_message", data)

# Function to get chat history using API
def get_chat_history(receiver_username, token):
    if not token:
        print("Token is invalid. Cannot fetch chat history.")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "receiver": receiver_username,
    }
    response = api_post("/api/get_chat_history/", data, headers=headers)
    return response.json()

def format_timestamp(timestamp):
    # Convert timestamp to a more readable format
    try:
        timestamp_obj = datetime.fromisoformat(timestamp)
        formatted_timestamp = timestamp_obj.strftime("%b %d, %Y %I:%M %p")
    except ValueError:
        formatted_timestamp = timestamp  # Use the original timestamp if it's not in the expected format
    return formatted_timestamp

def print_chat_history(chat_history, sender, receiver_username):
    init(autoreset=True)  # Initialize Colorama

    try:
        chat_messages = chat_history.get("chat_history", [])
        
        print(f"\nChat History between {sender} and {receiver_username}:\n")
        
        # Define text styles
        own_message_style = Fore.CYAN + Style.BRIGHT
        other_message_style = Fore.GREEN

        for message_json in chat_messages:
            message_data = json.loads(message_json)

            sender_username = message_data["sender_username"]
            content = message_data["content"]
            timestamp = message_data["timestamp"]

            # Format the timestamp
            formatted_timestamp = format_timestamp(timestamp)

            if sender_username == sender:
                formatted_message = f"{own_message_style}{sender} ({formatted_timestamp}): {content}"
                print(formatted_message)
            elif sender_username == receiver_username:
                formatted_message = f"{other_message_style}{receiver_username} ({formatted_timestamp}): {content}"
                print(formatted_message)
            print(Style.RESET_ALL)

    except json.JSONDecodeError:
        print("Invalid chat history JSON")

# Handle incoming messages from socket.io
@sio.on("receive_message")
def handle_received_message(data):
    sender = data.get('sender')
    content = data.get('content')

    if sender and content:
        print(f"Received message from {sender}: {content}")
    else:
        print("Incomplete message data received")

# Function to print online and offline users with colors
def print_online_users(online_users_response):
    online_users = online_users_response.get('online_users', [])
    if not online_users:
        print(f"{Fore.RED}No online users found.{Style.RESET_ALL}")
    else:
        for user in online_users:
            username = user.get("username", "Unknown")
            online = user.get("online", False)
            status = "Online" if online else "Offline"
            style = Fore.GREEN if online else Fore.RED
            formatted_user = f"{style}{username} ({status}){Style.RESET_ALL}"
            print(formatted_user)

def interactive_chat(user1_token, user2_token):
    try:
        while True:
            action = input("Select an action:\n1. Send message as User1\n2. Send message as User2\n3. View Chat History\n4. Get Suggested Friends\n5. Get Online Users\n6. Exit\n")

            if action == "1":
                message = input(f"Enter a message for {Config.USER2_USERNAME}: ")
                send_message(Config.USER1_USERNAME, Config.USER2_USERNAME, message)
            elif action == "2":
                message = input(f"Enter a message for {Config.USER1_USERNAME}: ")
                send_message(Config.USER2_USERNAME, Config.USER1_USERNAME, message)
            elif action == "3":
                user1_chat_history = get_chat_history(Config.USER2_USERNAME, user1_token)
                print_chat_history(user1_chat_history, Config.USER1_USERNAME, Config.USER2_USERNAME)
                user2_chat_history = get_chat_history(Config.USER1_USERNAME, user2_token)
                print_chat_history(user2_chat_history, Config.USER2_USERNAME, Config.USER1_USERNAME)
            elif action == "4":
                entered_user_id = input("Enter user_id (1,2,3,4, etc.): ")
                suggestions = get_suggested_friends(entered_user_id)
                print(f"Friends Suggestion for user_id: {entered_user_id}:\n")
                if suggestions:
                    for suggestion in suggestions:
                        friend_name = suggestion.get('friend_name')
                        explanation = suggestion.get('explanation')
                        formatted_suggestion = f"{Fore.YELLOW}Recommended Friend {friend_name}: {explanation}{Style.RESET_ALL}"
                        print(formatted_suggestion)
                else:
                    print(f"{Fore.RED}No friend suggestions found for user_id {entered_user_id}.{Style.RESET_ALL}")
            elif action == "5":
                online_users_response = get_online_users(user1_token)
                print("Online Users:")
                print_online_users(online_users_response)
            elif action == "6":
                break
            else:
                print("Invalid action. Please select 1, 2, 3, 4, 5, or 6.")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    register_user(Config.USER1_USERNAME, Config.USER1_PASSWORD)
    register_user(Config.USER2_USERNAME, Config.USER2_PASSWORD)
    user1_token = login_user(Config.USER1_USERNAME, Config.USER1_PASSWORD)
    user2_token = login_user(Config.USER2_USERNAME, Config.USER2_PASSWORD)
    
    if user1_token and user2_token:
        sio.connect(Config.BASE_URL)
        print(f"{Config.USER1_USERNAME} and {Config.USER2_USERNAME} connected to the Socket.IO server")
        
        interactive_chat(user1_token, user2_token)
        
        sio.disconnect()
        print(f"{Config.USER1_USERNAME} and {Config.USER2_USERNAME} disconnected from the Socket.IO server")
```

# /home/adimis/Desktop/chatapp/tests/interaction_test.py:
```py
import requests
import socketio
import time
import json
from colorama import init, Fore, Style
from datetime import datetime

# Initialize the socket.io client
sio = socketio.Client()

# Define the base URL for the Flask application
base_url = "http://localhost:5000"  # Replace with the actual URL

# Function to make HTTP POST requests
def post_request(endpoint, data, headers=None):
    try:
        response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request Error: {e}")
        return None

# Function to register a new user
def register_user(username, age, email, password, interests):
    data = {
        "username": username,
        "age": age,
        "email": email,
        "password": password,
        "interests": interests,
    }
    
    response = post_request("/api/register/", data)
    
    if response:
        print(f"User {username} registered successfully")
    else:
        print(f"Failed to register user {username}")

# Function to log in a user
def login_user(username, password):
    data = {
        "username": username,
        "password": password,
    }
    
    response = post_request("/api/login/", data)
    
    if response:
        token = response.json().get("access_token")
        print(f"User: {username} logged in successfully")
        return token
    else:
        print(f"Failed to log in user {username}")

# Function to send a message using socket.io
def send_message(username, receiver_username, message, token):
    if not token:
        # Token is not valid, do not send the message
        return
    
    data = {
        "username": username,
        "receiver": receiver_username,
        "message": message,
    }
    sio.emit("send_message", data)

# Function to get chat history using API
def get_chat_history(receiver_username, token):
    if not token:
        print("Token is invalid. Cannot fetch chat history.")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "receiver": receiver_username,
    }
    response = post_request("/api/get_chat_history/", data, headers=headers)
    return response

# Function to handle incoming messages from socket.io
@sio.on("receive_message")
def handle_received_message(data):
    sender = data.get('sender')
    receiver = data.get('receiver')
    content = data.get('content')

    if sender and content:
        print(f"Received message from {sender} to {receiver}: {content}")
    else:
        print("Incomplete message data received")

def user_workflow(username1, username2):
    try:
        # Connect to the Socket.IO server
        sio.connect(base_url)
        print(f"{username1} connected to the Socket.IO server")

        register_user(username1, 25, f"{username1}@example.com", "password1", ["chat"])
        token1 = login_user(username1, "password1")

        register_user(username2, 30, f"{username2}@example.com", "password2", ["chat"])
        token2 = login_user(username2, "password2")

        if token1 and token2:
            # Define an array of messages to be sent between users
            messages = [
                {"sender": username1, "receiver": username2, "content": "Hello"},
                {"sender": username2, "receiver": username1, "content": "Hi"},
                {"sender": username1, "receiver": username2, "content": "How are you?"},
                {"sender": username2, "receiver": username1, "content": "I'm good, thanks!"},
                {"sender": username1, "receiver": username2, "content": "Goodbye"},
                {"sender": username2, "receiver": username1, "content": "See you later"},
            ]

            for message in messages:
                send_message(message["sender"], message["receiver"], message["content"], token1 if message["sender"] == username1 else token2)
                print(f"{message['sender']} sent a message to {message['receiver']}: {message['content']}")
                time.sleep(1)  # Wait for a reply from the other user before sending the next message

            time.sleep(1)  # Wait for any pending messages to be received

            # Get chat history for both users
            res1 = get_chat_history(username2, token1)
            res2 = get_chat_history(username1, token2)

            if res1 and res2:
                chat_histories[username1]["chat_history"].extend(res1.json().get('chat_history'))
                chat_histories[username2]["chat_history"].extend(res2.json().get('chat_history'))
            else:
                print("Failed to fetch chat history for one or more users")

            # After workflow is completed, disconnect from the socket.io server
            sio.disconnect()
            print(f"{username1} disconnected from the Socket.IO server")

        else:
            print("User login failed. Cannot continue the workflow.")

    except Exception as e:
        print(f"An error occurred: {e}")

def format_timestamp(timestamp):
    # Convert timestamp to a more readable format
    try:
        timestamp_obj = datetime.fromisoformat(timestamp)
        formatted_timestamp = timestamp_obj.strftime("%b %d, %Y %I:%M %p")
    except ValueError:
        formatted_timestamp = timestamp  # Use the original timestamp if it's not in the expected format
    return formatted_timestamp

def print_chat_history(chat_history):
    init(autoreset=True)  # Initialize Colorama

    # Define text styles
    own_message_style = Fore.CYAN + Style.BRIGHT
    other_message_style = Fore.GREEN

    # Print the final chat histories between both users
    for username, data in chat_history.items():
        receiver = data["receiver"]
        messages = data["chat_history"]
        print(f"Chat history for {username} (with {receiver}):\n")
        for message_str in messages:
            message_data = json.loads(message_str)
            sender = message_data.get('sender_username')
            content = message_data.get('content')
            timestamp = message_data.get('timestamp')

            # Format the timestamp
            formatted_timestamp = format_timestamp(timestamp)

            if sender == username:  # Highlight the user's own messages
                formatted_message = f"{Style.BRIGHT}{sender} ({formatted_timestamp}): {content}"
                print(own_message_style + formatted_message)
            elif sender == receiver:  # Highlight messages from the other user
                formatted_message = f"{receiver} ({formatted_timestamp}): {content}"
                print(other_message_style + formatted_message)
            print(Style.RESET_ALL)  # Reset style to default

        print("\n")
      
if __name__ == "__main__":
    usernames = ["user1", "user2"]

    # Create a shared data structure for chat histories
    chat_histories = {
        usernames[0]: {
            "receiver": usernames[1],
            "chat_history": []
        },
        usernames[1]: {
            "receiver": usernames[0],
            "chat_history": []
        }
    }

    # Run the user workflow
    user_workflow(usernames[0], usernames[1])

    # Print chat history after the workflow is completed
    print_chat_history(chat_histories)
```

# /home/adimis/Desktop/chatapp/Dockerfile:
```Dockerfile
# Use the official Python image from Docker Hub
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Copy the .env file into the container
COPY .env .env

# Set environment variables from the .env file
ENV $(cat .env | xargs)

# Install required Python packages
RUN pip install -r requirements.txt

# Expose the port your Flask app will run on
EXPOSE 5000

# Command to start your application
CMD ["python", "run.py"]
```

# /home/adimis/Desktop/chatapp/.env.template:
```env
SECRET_KEY=
MONGODB_ATLAS_URI=
DATABASE_NAME=
USERS_COLLECTION=
CHAT_MESSAGES_COLLECTION=
```

# /home/adimis/Desktop/chatapp/run.py
```py
# run.py
from app import app, socketio

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
```

# /home/adimis/Desktop/chatapp/app/__init__.py:
```py
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
```

# /home/adimis/Desktop/chatapp/app/config.py:
```py
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGODB_ATLAS_URI = os.getenv("MONGODB_ATLAS_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    USERS_COLLECTION = os.getenv("USERS_COLLECTION")
    CHAT_MESSAGES_COLLECTION = os.getenv("CHAT_MESSAGES_COLLECTION")
```

# /home/adimis/Desktop/chatapp/app/socket_events/chat_events.py:
```py
# socket_events/chat_events.py
from app import socketio, app, users_collection
from app.services.database import db
from datetime import datetime
from flask import request
from app.models.message import Message
from flask_socketio import join_room, emit

@socketio.on('start_chat')
def handle_start_chat_event(data):
    sender_username = data["username"]
    receiver_username = data["receiver"]

    print("Sender: ", sender_username)

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
```

# /home/adimis/Desktop/chatapp/app/services/friend_recommendation.py:
```py
# app/services/recommendation.py
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json
import os

# Load user data from the JSON file.
file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'users.json')

with open(file_path, 'r') as json_file:
    users_data = json.load(json_file)

""" users.json file
{
    "users": [
        {
            "id": 1,
            "name": "User 1",
            "age": 81,
            "interests": {
                "singing": 91,
                "travelling": 88,
                "dancing": 37
            }
        },
        {
            "id": 2,
            "name": "User 2",
            "age": 46,
            "interests": {
                "cooking": 81,
                "computers": 18,
                "cars": 83
            }
        },
"""

# Function to get user's interests
def get_user_interests(user_id):
    user_index = user_id - 1  # User IDs are 1-based
    user_interests = users_data['users'][user_index]['interests']
    return user_interests

# Function to explain the recommendation
def explain_recommendation(user_id, recommended_friend_id):
    user_interests = get_user_interests(user_id)
    friend_interests = get_user_interests(recommended_friend_id)
    
    common_interests = set(user_interests.keys()) & set(friend_interests.keys())
    
    if not common_interests:
        explanation = "You both have no common interests."
    else:
        explanation = f"You have common interests in: {', '.join(common_interests)}"
    
    return explanation

# Preprocess the data
def preprocess_data(users_data):
    print("Preprocessing data...")
    # Convert user interests into a matrix
    interests_matrix = []
    for user in users_data['users']:
        interests_vector = [user['interests'].get(interest, 0) for interest in all_interests]
        interests_matrix.append(interests_vector)

    # Standardize age and interests
    age_vector = [user['age'] for user in users_data['users']]
    scaler = StandardScaler()
    age_vector = scaler.fit_transform(np.array(age_vector).reshape(-1, 1))
    interests_matrix = scaler.fit_transform(interests_matrix)

    return age_vector, interests_matrix

def hybrid_recommendation_with_explanations(user_id, users_data, age_vector, interests_matrix, top_n=5):
    user_index = user_id - 1  # User IDs are 1-based
    user_features = np.hstack([age_vector, interests_matrix])
    user_profile = user_features[user_index]

    similarities = cosine_similarity([user_profile], user_features)[0]
    similar_users_indices = np.argsort(similarities)[::-1]
    similar_users_indices = similar_users_indices[similar_users_indices != user_index]
    top_similar_users_indices = similar_users_indices[:top_n]

    recommendations_with_explanations = []

    for i in top_similar_users_indices:
        friend_id = users_data['users'][i]['id']
        friend_name = users_data['users'][i]['name']  # Get the friend's name
        explanation = explain_recommendation(user_id, friend_id)
        recommendations_with_explanations.append({'friend_name': friend_name, 'explanation': explanation})

    return recommendations_with_explanations

# Preprocess the data
print("Getting all interests...")
all_interests = set()
for user in users_data['users']:
    all_interests.update(user['interests'].keys())

age_vector, interests_matrix = preprocess_data(users_data)

# Function to get friend recommendations with explanations
def suggested_friends(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return json.dumps({'error': 'Invalid user_id'}), 400  # Return a JSON error response with a status code

    print(f"Received request for user {user_id}...")

    # Get friend recommendations with explanations
    recommendations_with_explanations = hybrid_recommendation_with_explanations(user_id, users_data, age_vector, interests_matrix)

    # Prepare the JSON response
    recommended_friends = [{'friend_name': recommendation['friend_name'], 'explanation': recommendation['explanation']} for recommendation in recommendations_with_explanations]

    response = {'recommended_friends': recommended_friends}

    return json.dumps(response), 200  # Return the JSON response with a 200 status code
```

# /home/adimis/Desktop/chatapp/app/routes/auth.py:
```py
# routes/auth.py
from flask import request, jsonify, Blueprint
from app.services.auth import register_user, login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register/', methods=['POST'])
def register():
    data = request.json
    result, status_code = register_user(data)
    return jsonify(result), status_code

@auth_bp.route('/api/login/', methods=['POST'])
def login():
    data = request.json
    result, status_code = login_user(data)
    return jsonify(result), status_code
```

# /home/adimis/Desktop/chatapp/app/routes/chat.py:
```py
# app/routes/chat.py
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import users_collection
from app.services.chat import get_user_chat_history

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/online-users/')
@jwt_required()
def get_online_users():
    online_users = users_collection.find({"online": True}, {"_id": 0, "password": 0})
    online_user_list = list(online_users)
    return jsonify({"online_users": online_user_list}), 200

@chat_bp.route('/api/get_chat_history/', methods=['POST'])
@jwt_required()
def get_chat_history():
    try:
        data = request.json
        sender_username = get_jwt_identity()
        receiver_username = data.get('receiver')

        if not receiver_username:
            return jsonify({"message": "Receiver username is required"}), 400

        chat_history = get_user_chat_history(sender_username, receiver_username)

        if chat_history is not None:
            return jsonify({"chat_history": chat_history}), 200
        else:
            return jsonify({"message": "An error occurred while retrieving chat history"}), 500
    except Exception as e:
        print(f"Unexpected error in get_chat_history: {str(e)}")
        return jsonify({"message": "An unexpected error occurred"}), 500
```

# /home/adimis/Desktop/chatapp/app/routes/friend_recommendation.py:
```py
# app/routes/friend_recommendation.py
from flask import Blueprint
from app.services.friend_recommendation import suggested_friends

friend_rec_bp = Blueprint('friend_recommendation', __name__)

@friend_rec_bp.route('/api/suggested-friends/<user_id>', methods=['GET'])
def friend_recommendation_system(user_id):
    recommendations = suggested_friends(user_id)
    return recommendations
```