import requests
import json
import socketio

# Initialize the socket.io client
sio = socketio.Client()

# Define the base URL for the Flask application
base_url = "http://localhost:5000"  # Replace with the actual URL

# Define the token as a global variable
token = None

# Function to register a new user
def register_user(username, age, email, password, interests):
    data = {
        "username": username,
        "age": age,
        "email": email,
        "password": password,
        "interests": interests,
    }
    response = requests.post(f"{base_url}/api/register/", json=data)
    return response

# Function to log in a user
def login_user(username, password):
    global token  # Declare token as a global variable
    data = {
        "username": username,
        "password": password,
    }
    response = requests.post(f"{base_url}/api/login/", json=data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("User logged in successfully")
    else:
        print("Failed to log in user")
    return response

# Function to test friend recommendation system
def test_get_suggested_friends(user_id):
    # Send a GET request to the server to get suggested friends for the user with the given user_id
    response = requests.get(f'{base_url}/api/suggested-friends/{user_id}')

    # Check the response status code
    if response.status_code == 200:
        # If the status code is 200 (OK), parse the JSON response
        data = response.json()

        # Check if the response contains the 'recommended_friends' key
        if 'recommended_friends' in data:
            recommended_friends = data['recommended_friends']
            print(f'\nRecommended Friends for User {user_id}:')
            for friend in recommended_friends:
                friend_id = friend['friend_id']
                explanation = friend['explanation']
                print(f'Friend ID: {friend_id}, Explanation: {explanation}')
        else:
            print('\nError: Response does not contain recommended_friends')
    elif response.status_code == 404:
        print(f'\nError: User with ID {user_id} not found')
    else:
        print(f'\nError: Request failed with status code {response.status_code}')

# Function to get a list of online users
def get_online_users():
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(f"{base_url}/api/online-users/", headers=headers)
    return response

# Function to send a message using socket.io
def send_message(username, receiver_username, message):
    data = {
        "username": username,
        "receiver": receiver_username,
        "message": message,
    }
    sio.emit("send_message", data)

# Function to handle incoming messages from socket.io
@sio.on("receive_message")
def handle_received_message(data):
    sender = data.get('sender')  # Use .get() to safely access dictionary keys
    receiver = data.get('receiver')
    content = data.get('content')

    if sender and content:
        # Print the received message
        print(f"\nReceived message from {sender}: {content}")

        # Print the chat history
        chat_history_response = get_chat_history(receiver)  # Call the API to get chat history
        if chat_history_response.status_code == 200:
            chat_history = chat_history_response.json().get("chat_history", [])
            
            print("\nChat History:")
            for message in chat_history:
                message_data = json.loads(message)
                sender = message_data.get("sender_username")
                receiver = message_data.get("receiver_username")
                content = message_data.get("content")
                timestamp = message_data.get("timestamp")
                
                print(f"\nSender: {sender}")
                print(f"Receiver: {receiver}")
                print(f"Content: {content}")
                print(f"Timestamp: {timestamp}")
                
        else:
            print("\nFailed to fetch chat history")
    else:
        print("\nIncomplete message data received")

# Function to get chat history using API
def get_chat_history(receiver_username):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "receiver": receiver_username,
    }
    response = requests.post(f"{base_url}/api/get_chat_history/", headers=headers, json=data)
    return response

# Function to handle error messages from socket.io
@sio.on("error_message")
def handle_error_message(data):
    print(f"\nError: {data['message']}")

# Main function to test the workflow
def main():
    username = input("Enter your username: ")
    email = None
    interests = None
    age = None
    if username == "damon":
        email = "damon@gmail.com"
        age = "22"
        interests = {
            "singing": 91,
            "travelling": 88,
            "dancing": 37,
            "swimming": 89,
            "cooking": 78,
            "computers": 78,
            "cars": 78,
            "music": 78,
            "movies": 78,
            "photography": 78,
            "drawing": 78,
        }
    else:
        email = "dragneel@gmail.com"
        age = "25"
        interests = {
            "cooking": 81,
            "computers": 18,
            "cars": 83,
            "swimming": 89,
            "dancing": 78,
        }

    password = "test_password"

    # Register a new user
    register_response = register_user(username, age, email, password, interests)
    if register_response.status_code == 200:
        print("\nUser registered successfully")
    else:
        print("\nFailed to register user")
        return

    # Log in the user
    login_response = login_user(username, password)
    if login_response.status_code == 200:
        print("\nUser logged in successfully")
    else:
        print("\nFailed to log in user")
        return

    # Get a list of online users
    online_users_response = get_online_users()
    if online_users_response.status_code == 200:
        online_users = online_users_response.json().get("online_users", [])
        print("\nOnline users:", online_users)
    else:
        print("\nFailed to get online users")

    # Start a chat with another user (enter the receiver's username)
    receiver_username = input("\nEnter the username of the receiver: ")

    # Connect to the Socket.IO server
    sio.connect(base_url)

    # Emit the 'start_chat' event to the server
    sio.emit("start_chat", {"username": username, "receiver": receiver_username})

    # Send a message (enter the message to send)
    while True:
        message = input("\nEnter a message (or 'exit' to quit): ")
        if message == "exit":
            break
        send_message(username, receiver_username, message)

    # Disconnect from the Socket.IO server
    sio.disconnect()

if __name__ == "__main__":
    #test_get_suggested_friends(123)
    main()
