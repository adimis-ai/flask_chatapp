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
