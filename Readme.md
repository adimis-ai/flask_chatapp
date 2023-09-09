# Flask Chat Application Documentation

## Introduction

Welcome to the documentation for the Flask Chat Application. This chat application is built using Flask and enables users to create accounts, log in, view online users, initiate chats with online users, and send messages in real-time. The documentation covers the API endpoints, functionality, and recommended algorithms.

## Table of Contents

1. [API Endpoints](#api-endpoints)
   - [User Registration](#user-registration)
   - [User Login](#user-login)
   - [Get Online Users](#get-online-users)
   - [Get All Chats](#get-all-chats)
   - [Get Chat](#get-all-chats)
   - [Start a Chat](#start-a-chat)
   - [Send a Message](#send-a-message)
   - [Friends Recommendation](#friends-recommendation)

2. [Implementation Details](#implementation-details)
   - [User Registration](#user-registration-implementation)
   - [User Login](#user-login-implementation)
   - [Get Online Users](#get-online-users-implementation)
   - [Get All Chats](#get-all-chats-implementation)
   - [Get Chat](#get-all-chats-implementation)
   - [Start a Chat](#start-a-chat-implementation)
   - [Send a Message](#send-a-message-implementation)
   - [Friends Recommendation](#friends-recommendation-implementation)

## API Endpoints

### User Registration

- **Endpoint**: `POST /api/register/`
- **Functionality**: Allows users to create an account by providing necessary information such as username, email, and password.
- **Input**: `RegistrationRequest` data.
- **Output**: 
  - If the registration is successful, return a success message or status code.
  - If there are validation errors or the username/email is already taken, return appropriate error messages or status codes.

### User Login

- **Endpoint**: `POST /api/login/`
- **Functionality**: Allows users to log in to their account by providing their credentials (username/email and password).
- **Input**: `LoginRequest` data.
- **Output**:
  - If the login is successful, return an authentication token or a success message with the user details.
  - If the credentials are invalid, return an error message or status code.

### Get Online Users

- **Endpoint**: `GET /api/online-users/`
- **Functionality**: Retrieves a list of all online users who are currently available for chat.
- **Input**: None.
- **Output**:
  - Returns a list of online user objects with their details, such as username and status.

### Get all Chats of the User:

- **Endpoint**: `GET /api/chats/`
- **Functionality**: Retrieves a list of all chat conversations for the currently authenticated user.
- **Input**: None.
- **Output**:
  - Returns a list of chat objects, each containing details of the chat, including its ID, participant IDs, and the last message in the conversation.

### Get Chat:

- **Endpoint**: `GET /api/chat/<chat_id>`
- **Functionality**: Retrieves the details of a specific chat conversation identified by its `chat_id`.
- **Input**: Chat ID as a parameter.
- **Output**:
  - Returns a chat object containing details of the chat, including its ID, participant IDs, and the list of messages in the conversation.

### Start a Chat

- **Endpoint**: `POST /api/chat/start/`
- **Functionality**: Allows a user to initiate a chat with another user who is online and available.
- **Input**: `ChatStartRequest` data.
- **Output**:
  - If the recipient is online and available, return a success message or status code.
  - If the recipient is offline or unavailable, return an error message or status code.

### Send a Message

- **Endpoint**: `WEBSOCKET /api/chat/send/`
- **Functionality**: Allows a user to send and receive instant messages to another user who is online.
- **Input**: WebSocket connection, `MessageSendRequest` data.
- **Output**: WebSocket communication to send messages in real-time.
- Description: Handles real-time message communication between users.

### Friends Recommendation

- **Endpoint**: `GET /api/suggested-friends/<user_id>`
- **Functionality**: Allows sending a GET request to the application with a user_id and returns the top 5 recommended friends for that user.
- **Note**: This is a public API, and the user does not need to be signed in. Operations are not related to the application’s DB.
- **Input**: User ID as a parameter.
- **Output**: A JSON containing 5 user instances based on your recommendation algorithm.

## Implementation Details:

### User Registration (Implementation)

1. **Collect User Information**: Receive user registration data (username, email, password) through a POST request.

2. **Validation**: Check if the provided data meets validation criteria. Ensure that the username and email are unique, and the password meets security requirements.

3. **Database Interaction**: Insert the new user's data into the database. Typically, hash the password before storing it for security.

4. **Response**: Respond with a success message or status code if registration is successful. Provide appropriate error messages or status codes for validation failures.

### User Login (Implementation)

1. **Collect Login Information**: Receive user login data (username or email, password) through a POST request.

2. **Authentication**: Validate the provided credentials by checking them against the stored user data in the database. Generate an authentication token (e.g., JWT) upon successful authentication.

3. **Response**: If authentication is successful, respond with an access token and user details in a `LoginResponse`. For invalid credentials, return an error message or status code.

### Get Online Users (Implementation)

1. **Database Query**: Query the database to find users with an `online` status set to `True`.

2. **User Details**: Retrieve relevant user details (e.g., ID, username) for the online users found.

3. **Response**: Create an `OnlineUsersResponse` with the list of online user details and return it as a JSON response.

### Get all Chats of the User (Implementation)

1. **Authentication**: Ensure that the user making the request is authenticated and authorized to access their chat conversations.

2. **Database Query**: Query the database to retrieve all chat conversations associated with the authenticated user. You will use the User model's chats field, which contains the IDs of the user's chats.

3. **Response**: Create a response containing a list of chat objects, each representing a chat conversation. Include details such as the chat ID, participant IDs, and the last message in the chat. Return this response as a JSON object.

### Get Chat (Implementation):

1. **Authentication**: Ensure that the user making the request is authenticated and authorized to access the specified chat conversation.

2. **Database Query**: Query the database to retrieve the chat conversation identified by the provided `chat_id`.

3. **Response**: Create a response containing details of the chat conversation, including its ID, participant IDs, and the list of messages in the conversation. Return this response as a JSON object.

### Start a Chat (Implementation)

1. **Collect Recipient Information**: Receive a `ChatStartRequest` with the recipient's user ID through a POST request.

2. **Database Update**: If the recipient is available, create a new chat record in the database. This record typically includes the IDs of both the sender and the recipient and an empty message list.

3. **Response**: Respond with a `ChatStartResponse` containing details of the newly created chat, such as its ID and participant IDs.

### Send a Message (Implementation)

1. **WebSocket Communication**: Implement a WebSocket handler to manage WebSocket connections. Receive message data through WebSocket when a user sends a message.

2. **Validation**: Validate the received message data to ensure it adheres to the required format and security standards.

3. **Recipient Availability**: Ensure that users cannot send messages to offline users by validating the recipient's online status before sending the message.

4. **Real-time Delivery**: Use the WebSocket connection to send the message to the intended recipient in real-time. Update the chat's message history in the database to record the message.

### Friends Recommendation (Implementation)

1. **User Data Retrieval**: Retrieve the user's profile data based on the provided `user_id` from your dataset.

2. **Similarity Calculation**: Implement a recommendation algorithm that calculates user similarity with other users. This typically involves comparing interests and age.

3. **Combine Scores**: Combine the similarity scores from content-based and collaborative filtering approaches, adjusting weights if necessary.

4. **Sorting and Selection**: Sort the users by their combined similarity scores in descending order. Select the top 5 users as recommended friends.

## Conclusion:

This documentation provides an overview of the Flask Chat Application, its API endpoints, and implementation details. It serves as a guide for developers and users to understand and use the application effectively.

## User Friends Data:
``json
{
    "users": [
        {
            "id": 1,
            "name": "User 1",
            "age": 81,
            "interests": {
                "singing": 91,
                "travelling": 88,
                "dancing": 37
            }
        },
        {
            "id": 2,
            "name": "User 2",
            "age": 46,
            "interests": {
                "cooking": 81,
                "computers": 18,
                "cars": 83
            }
        },
        {
            "id": 3,
            "name": "User 3",
            "age": 79,
            "interests": {
                "travelling": 37,
                "dancing": 29,
                "computers": 36,
                "cars": 10,
                "cooking": 37
            }
        },
        {
            "id": 4,
            "name": "User 4",
            "age": 11,
            "interests": {
                "music": 61,
                "photography": 46,
                "dancing": 93,
                "drawing": 41,
                "cars": 72
            }
        },
]}
```