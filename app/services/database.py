# app/services/database.py
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import json_util
from app.models.message import Message
from app import users_collection, chat_messages_collection

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
            chat_messages_collection.insert_one(message.to_dict())

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