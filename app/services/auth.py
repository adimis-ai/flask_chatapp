# services/auth.py
from app.models.user import User
from app.services.database import db
from datetime import datetime
from app import users_collection, bcrypt
from flask_jwt_extended import create_access_token

def register_user(data):
    username = data['username']
    email = data['email']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    age = data['age']
    interests = data.get('interests', {})

    print(f"Registering user: username={username}, email={email}")

    # Check if a user with the same email or username already exists
    existing_user_by_email = db.get_user_by_email(email)
    existing_user_by_username = db.get_user_by_username(username)

    if existing_user_by_email:
        return {"error": "Email already exists. Please use a different email."}, 400
    elif existing_user_by_username:
        return {"error": "Username already exists. Please choose a different username."}, 400

    # If no user with the same email or username exists, create a new user
    new_user = User(username, age, email, password)
    new_user.interests = interests

    # Set online status and last_activity
    new_user.online = True
    new_user.last_activity = datetime.now()

    if db.create_user(new_user.to_dict()):
        print("User registered successfully")
        return {"message": "User registered successfully"}, 200
    else:
        print("Username or email already exists")
        return {"error": "Registration failed. Please try again later."}, 500

def login_user(data):
    username = data['username']
    password = data['password']

    print(f"Logging in user: username={username}")

    user = db.get_user_by_username(username)

    if user and bcrypt.check_password_hash(user['password'], password):
        print("Login successful")

        # Set online status and last_activity
        users_collection.update_one({"username": username}, {"$set": {"online": True, "last_activity": datetime.now()}})

        access_token = create_access_token(identity=username)
        return {"message": "Login successful", "access_token": access_token}, 200
    else:
        print("Invalid credentials")
        return {"error": "Invalid username or password. Please try again."}, 401
