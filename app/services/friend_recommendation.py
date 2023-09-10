# app/services/recommendation.py
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json
import os

# Load user data from the JSON file.
file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'users.json')

with open(file_path, 'r') as json_file:
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
        return json.dumps({'error': 'Invalid user_id'}), 400  # Return a JSON error response with a status code

    print(f"Received request for user {user_id}...")

    # Get friend recommendations with explanations
    recommendations_with_explanations = hybrid_recommendation_with_explanations(user_id, users_data, age_vector, interests_matrix)

    # Prepare the JSON response
    recommended_friends = [{'friend_id': recommendation['friend_id'], 'explanation': recommendation['explanation']} for recommendation in recommendations_with_explanations]

    response = {'recommended_friends': recommended_friends}

    return json.dumps(response), 200  # Return the JSON response with a 200 status code
