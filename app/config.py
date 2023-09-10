# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGODB_ATLAS_URI = os.getenv("MONGODB_ATLAS_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    USERS_COLLECTION = os.getenv("USERS_COLLECTION")
    CHAT_MESSAGES_COLLECTION = os.getenv("CHAT_MESSAGES_COLLECTION")
