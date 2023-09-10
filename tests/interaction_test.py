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
