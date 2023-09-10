# app/routes/friend_recommendation.py
from flask import Blueprint
from app.services.friend_recommendation import suggested_friends

friend_rec_bp = Blueprint('friend_recommendation', __name__)

@friend_rec_bp.route('/api/suggested-friends/<user_id>', methods=['GET'])
def friend_recommendation_system(user_id):
    recommendations = suggested_friends(user_id)
    return recommendations
