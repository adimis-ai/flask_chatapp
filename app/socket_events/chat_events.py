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
