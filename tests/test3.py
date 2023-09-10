import requests
import json
import socketio
import logging
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

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions for API requests
def api_post(endpoint, data=None, headers=None):
    url = f"{Config.BASE_URL}/{endpoint}"
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP Request Error: {e}")
        return None

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
        logger.info(f"User: {username} logged in successfully")
        return token
    else:
        logger.error(f"Failed to log in user {username}")

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
        logger.info(f"Received message from {sender}: {content}")
    else:
        logger.warning("Incomplete message data received")

def interactive_chat(user1_token, user2_token):
    try:
        while True:
            action = input("Select an action:\n1. Send message as User1\n2. Send message as User2\n3. View Chat History\n4. Exit\n")
            
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
                break
            else:
                logger.warning("Invalid action. Please select 1, 2, 3, or 4.")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    register_user(Config.USER1_USERNAME, Config.USER1_PASSWORD)
    register_user(Config.USER2_USERNAME, Config.USER2_PASSWORD)
    user1_token = login_user(Config.USER1_USERNAME, Config.USER1_PASSWORD)
    user2_token = login_user(Config.USER2_USERNAME, Config.USER2_PASSWORD)
    
    if user1_token and user2_token:
        sio.connect(Config.BASE_URL)
        logger.info(f"{Config.USER1_USERNAME} and {Config.USER2_USERNAME} connected to the Socket.IO server")
        
        interactive_chat(user1_token, user2_token)
        
        sio.disconnect()
        logger.info(f"{Config.USER1_USERNAME} and {Config.USER2_USERNAME} disconnected from the Socket.IO server")
