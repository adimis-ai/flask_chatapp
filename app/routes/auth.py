# routes/auth.py
from flask import request, jsonify, Blueprint
from app.services.auth import register_user, login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register/', methods=['POST'])
def register():
    data = request.json
    result, status_code = register_user(data)
    return jsonify(result), status_code

@auth_bp.route('/api/login/', methods=['POST'])
def login():
    data = request.json
    result, status_code = login_user(data)
    return jsonify(result), status_code
