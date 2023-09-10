# services/chat.py
from app.services.database import db
from pymongo.errors import PyMongoError

def get_user_chat_history(sender_username, receiver_username):
    try:
        print(f"Retrieving chat history for sender {sender_username} and receiver {receiver_username}")

        # Retrieve the chat history for the sender and receiver
        chat_history = db.get_chat_history(sender_username, receiver_username)

        print("Chat history retrieved successfully.", chat_history)

        return chat_history
    except PyMongoError as e:
        print(f"Error in get_user_chat_history: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_user_chat_history: {str(e)}")
        return None
