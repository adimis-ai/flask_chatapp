# app/routes/chat.py
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import users_collection
from app.services.chat import get_user_chat_history

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/online-users/')
@jwt_required()
def get_online_users():
    online_users = users_collection.find({"online": True}, {"_id": 0, "password": 0})
    online_user_list = list(online_users)
    return jsonify({"online_users": online_user_list}), 200

@chat_bp.route('/api/get_chat_history/', methods=['POST'])
@jwt_required()
def get_chat_history():
    try:
        data = request.json
        sender_username = get_jwt_identity()
        receiver_username = data.get('receiver')

        if not receiver_username:
            return jsonify({"message": "Receiver username is required"}), 400

        chat_history = get_user_chat_history(sender_username, receiver_username)

        if chat_history is not None:
            return jsonify({"chat_history": chat_history}), 200
        else:
            return jsonify({"message": "An error occurred while retrieving chat history"}), 500
    except Exception as e:
        print(f"Unexpected error in get_chat_history: {str(e)}")
        return jsonify({"message": "An unexpected error occurred"}), 500
