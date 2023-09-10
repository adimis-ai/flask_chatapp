# app/models/user.py
class User:
    def __init__(self, username, age, email, password):
        self.username = username
        self.age = age
        self.email = email
        self.password = password
        self.online = False
        self.last_activity = None

    def to_dict(self):
        # Convert the User object to a dictionary
        return {
            "username": self.username,
            "age": self.age,
            "email": self.email,
            "password": self.password,
            "online": self.online,
            "last_activity": self.last_activity,
        }