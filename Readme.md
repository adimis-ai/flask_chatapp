# Flask Chat Application Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Project Overview](#project-overview)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Endpoints](#endpoints)
6. [Socket.IO Events](#socketio-events)
7. [Friend Recommendation System](#friend-recommendation-system)
8. [Testing](#testing)

---

## 1. Introduction <a name="introduction"></a>

This documentation provides a detailed overview of the Flask Chat Application project. The project consists of a Flask-based chat application with real-time messaging capabilities using Socket.IO. Additionally, it includes a friend recommendation system based on user interests.

## 2. Project Overview <a name="project-overview"></a>

The Chat Application project consists of three main components:

- `app.py`: The Flask application that handles user registration, login, real-time messaging, and friend recommendation system integration.
- `friend_rec_sys.py`: The friend recommendation system module that suggests friends for users based on their interests.
- `test.py`: A testing script that allows users to interact with the chat application, register, log in, send messages, and receive friend recommendations.

The project's key features include user registration, login, real-time messaging using Socket.IO, online/offline status tracking, and friend recommendations with explanations based on user interests.

## 3. Installation <a name="installation"></a>

To set up and run the Chat Application project, follow these steps:

1. Clone the project repository:

   ```
   git clone <repository_url>
   ```

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Ensure you have MongoDB installed and running. You can either set up a local MongoDB instance or use a cloud-based service like MongoDB Atlas.

4. Update the MongoDB connection string in `app.py` to point to your MongoDB instance:

   ```python
   client = MongoClient("mongodb+srv://<username>:<password>@<cluster_url>/<db_name>?retryWrites=true&w=majority")
   ```

5. Run the Flask application:

   ```
   python app.py
   ```

6. In a separate terminal, run the Socket.IO server:

   ```
   python -m flask run --host=0.0.0.0 --port=5000
   ```

7. Open another terminal and run the testing script:

   ```
   python test.py
   ```

## 4. Usage <a name="usage"></a>

Once the project is set up, you can use the testing script (`test.py`) to interact with the chat application. Follow the prompts to register, log in, send messages, and receive friend recommendations.

## 5. Endpoints <a name="endpoints"></a>

The Flask application (`app.py`) exposes the following API endpoints:

- `/api/register/` (POST): Allows users to register with their username, age, email, password, and interests.
- `/api/login/` (POST): Allows users to log in with their username and password.
- `/api/online-users/` (GET): Returns a list of online users for the authenticated user.
- `/api/get_chat_history/` (POST): Returns the chat history between the authenticated user and a specified receiver.

## 6. Socket.IO Events <a name="socketio-events"></a>

The chat application uses Socket.IO for real-time messaging. It includes the following Socket.IO events:

- `start_chat`: Initiates a chat session between two users.
- `send_message`: Sends a message from one user to another.
- `receive_message`: Receives a message in real-time.
- `chat_started`: Indicates that a chat session has started successfully.
- `chat_error`: Indicates an error in starting a chat session.

## 7. Friend Recommendation System <a name="friend-recommendation-system"></a>

The friend recommendation system (`friend_rec_sys.py`) provides friend recommendations based on user interests. It includes the following components:

- User interests are loaded from a JSON file (`users.json`) during initialization.
- `get_user_interests(user_id)`: Retrieves interests for a specific user.
- `explain_recommendation(user_id, recommended_friend_id)`: Generates an explanation for a friend recommendation based on common interests.
- `preprocess_data(users_data)`: Standardizes age and interests data for recommendation.
- `hybrid_recommendation_with_explanations(user_id, users_data, age_vector, interests_matrix, top_n=5)`: Recommends friends with explanations using a hybrid recommendation approach.
- `suggested_friends(user_id)`: Exposes an API endpoint to retrieve friend recommendations with explanations for a given user ID.

## 8. Testing <a name="testing"></a>

The testing script (`test.py`) allows you to interact with the chat application. You can register, log in, send messages, and receive friend recommendations. To test the friend recommendation system, you can uncomment the `test_get_suggested_friends(user_id)` function call in the script.