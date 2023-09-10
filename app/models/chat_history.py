# app/models/chat_history.py
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