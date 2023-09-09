import json
import numpy as np
from flask import Flask, jsonify, request
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

# Load user data from the JSON file.
with open('users.json', 'r') as json_file:
    users_data = json.load(json_file)

# Function to get user's interests
def get_user_interests(user_id):
    user_index = user_id - 1  # User IDs are 1-based
    user_interests = users_data['users'][user_index]['interests']
    return user_interests

# Function to explain the recommendation
def explain_recommendation(user_id, recommended_friend_id):
    user_interests = get_user_interests(user_id)
    friend_interests = get_user_interests(recommended_friend_id)
    
    common_interests = set(user_interests.keys()) & set(friend_interests.keys())
    
    if not common_interests:
        explanation = "You both have no common interests."
    else:
        explanation = f"You have common interests in: {', '.join(common_interests)}"
    
    return explanation

# Preprocess the data
def preprocess_data(users_data):
    print("Preprocessing data...")
    # Convert user interests into a matrix
    interests_matrix = []
    for user in users_data['users']:
        interests_vector = [user['interests'].get(interest, 0) for interest in all_interests]
        interests_matrix.append(interests_vector)

    # Standardize age and interests
    age_vector = [user['age'] for user in users_data['users']]
    scaler = StandardScaler()
    age_vector = scaler.fit_transform(np.array(age_vector).reshape(-1, 1))
    interests_matrix = scaler.fit_transform(interests_matrix)

    return age_vector, interests_matrix

def hybrid_recommendation_with_explanations(user_id, users_data, age_vector, interests_matrix, top_n=5):
    user_index = user_id - 1  # User IDs are 1-based
    user_features = np.hstack([age_vector, interests_matrix])
    user_profile = user_features[user_index]

    similarities = cosine_similarity([user_profile], user_features)[0]
    similar_users_indices = np.argsort(similarities)[::-1]
    similar_users_indices = similar_users_indices[similar_users_indices != user_index]
    top_similar_users_indices = similar_users_indices[:top_n]

    recommendations_with_explanations = []

    for i in top_similar_users_indices:
        friend_id = users_data['users'][i]['id']
        explanation = explain_recommendation(user_id, friend_id)
        recommendations_with_explanations.append({'friend_id': friend_id, 'explanation': explanation})

    return recommendations_with_explanations

# Preprocess the data
print("Getting all interests...")
all_interests = set()
for user in users_data['users']:
    all_interests.update(user['interests'].keys())

age_vector, interests_matrix = preprocess_data(users_data)

# Function to get friend recommendations with explanations
def suggested_friends(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user_id format'}), 400

    print(f"Received request for user {user_id}...")

    if user_id not in [user['id'] for user in users_data['users']]:
        print(f"User {user_id} not found in the data...")
        return jsonify({'error': 'User not found'}), 404

    recommendations_with_explanations = hybrid_recommendation_with_explanations(user_id, users_data, age_vector, interests_matrix)
    
    result = {'recommended_friends': recommendations_with_explanations}
    
    return jsonify(result)


