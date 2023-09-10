# app/models/message.py
from datetime import datetime

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