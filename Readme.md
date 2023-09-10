# ChatApp Prototype Documentation

This documentation provides a comprehensive overview of the ChatApp prototype, a Flask-based web application with real-time chat functionality using Socket.IO and MongoDB Atlas for data storage. The application is designed for users to register, log in, and communicate with each other in real-time through chat messages.

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Configuration](#configuration)
5. [Setup](#setup)
6. [Usage](#usage)
7. [Automated Tests](#automated-tests)
8. [Interactions Test](#interactions-test)
9. [Docker Integration](#docker-integration)

## 1. Introduction<a name="introduction"></a>

The ChatApp prototype is a web-based application that allows users to register, log in, and communicate with each other using real-time chat messages. It is built using Flask, Socket.IO for real-time communication, and MongoDB Atlas as the database to store user information and chat messages.

Key features of the ChatApp prototype include:

- User registration and login.
- Real-time chat messaging.
- Fetching chat history.
- Friend recommendation system.

## 2. Prerequisites<a name="prerequisites"></a>

Before running the ChatApp prototype, ensure that you have the following prerequisites installed on your system:

- Python 3.10
- Pip
- Docker (optional, for Docker integration)

## 3. Project Structure<a name="project-structure"></a>

The ChatApp prototype project structure is organized as follows:

```
/chatapp
    ├── Dockerfile
    ├── .env.template
    ├── requirements.txt
    ├── run.py
    ├── app/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── services/
    │   │   ├── auth.py
    │   │   ├── chat.py
    │   │   ├── database.py
    │   │   ├── friend_recommendation.py
    │   │   └── ...
    │   ├── routes/
    │   │   ├── auth.py
    │   │   ├── chat.py
    │   │   ├── friend_recommendation.py
    │   │   └── ...
    │   ├── socket_events/
    │   │   ├── chat_events.py
    │   │   └── ...
    │   ├── models/
    │   │   ├── message.py
    │   │   └── ...
    ├── tests/
    │   ├── automated_test.py
    │   └── interaction_test.py
```

- `Dockerfile`: Configuration file for Docker containerization.
- `.env.template`: Template for environment variables.
- `requirements.txt`: List of Python dependencies.
- `run.py`: Entry point for the Flask application.

The `app/` directory contains the main application code and is further divided into subdirectories based on functionality:

- `services/`: Contains modules for various services such as authentication, chat, database, and friend recommendation.
- `routes/`: Defines API routes for user authentication, chat functionality, and friend recommendations.
- `socket_events/`: Handles real-time socket events for chat functionality.
- `models/`: Contains data models, such as the `Message` model.

The `tests/` directory includes automated and interaction test scripts.

## 4. Configuration<a name="configuration"></a>

### Environment Variables

The ChatApp prototype uses environment variables for configuration. You can create a `.env` file in the root directory based on the provided `.env.template` and populate it with the following variables:

- `SECRET_KEY`: A secret key for Flask session management.
- `MONGODB_ATLAS_URI`: MongoDB Atlas connection URI.
- `DATABASE_NAME`: Name of the MongoDB database.
- `USERS_COLLECTION`: Name of the collection for storing user data.
- `CHAT_MESSAGES_COLLECTION`: Name of the collection for storing chat messages.

Ensure you set appropriate values for these variables in the `.env` file.

## 5. Setup<a name="setup"></a>

To set up and run the ChatApp prototype, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/chatapp.git
   ```

2. Navigate to the project directory:

   ```bash
   cd chatapp
   ```

3. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:

   - **Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **Linux/macOS:**

     ```bash
     source venv/bin/activate
     ```

5. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

6. Create a copy of the `.env.template` file and rename it to `.env`. Populate it with appropriate values for the environment variables as mentioned in the [Configuration](#configuration) section.

## 6. Usage<a name="usage"></a>

### Running the Application

To run the ChatApp prototype, execute the following command:

```bash
python run.py
```

The application will start, and you can access it in your web browser at `http://localhost:5000`.

### User Registration and Login

- Register a new user by navigating to the registration page and providing the required details.
- Log in with the registered user credentials.

### Real-Time Chat

- After logging in, you can initiate real-time chat with other users who are online.
- Enter the receiver's username and start a chat.
- Send and receive chat messages in real-time using the chat interface.

### Chat History

- You can fetch chat history with a specific user by selecting the "View Chat History" option.
- The chat history will display the previous chat messages between you and the selected user.

### Friend Recommendation

- To get friend recommendations, select the "Get Suggested Friends" option.
- Enter the user ID (1, 2, 3, etc.) for which you want to receive friend recommendations.
- The application will provide friend recommendations based on common interests.

## 7. Automated Tests<a name="automated-tests"></a>

The ChatApp prototype is equipped with a suite of automated tests meticulously designed to validate the application's functionality. These tests are organized within the `tests/` directory, ensuring thorough examination of various components and features:

- `automated_test.py`: This script houses a comprehensive set of automated tests that scrutinize API endpoints and the core functionality of the application. These tests encompass critical aspects such as user registration, login, chat messaging, and retrieval of chat history.

To execute the suite of automated tests, execute the following command in your terminal:

```bash
python tests/automated_test.py
```

These tests serve as a robust safety net, confirming that fundamental functionalities operate as intended.

## 8. Interactions Test<a name="interactions-test"></a>

The `interaction_test.py` script is tailored to emulate user interactions within the ChatApp prototype. This suite of tests assesses the real-time chat functionality by simulating user behaviors, including sending and receiving messages, as well as retrieving chat history.

To launch the interactions test and observe how users interact with the application:

```bash
python tests/interaction_test.py
```

his test will simulate user interactions with the application and validate the behavior of real-time chat and chat history features.

## 9. Docker Integration<a name="docker-integration"></a>

The ChatApp prototype can also be containerized using Docker. A `Dockerfile` is provided in the project directory for this purpose. You can build and run the Docker container as follows:

1. Build the Docker image:

   ```bash
   docker build -t chatapp-image .
   ```

2. Run the Docker container:

   ```bash
   docker run -p 5000:5000 --env-file .env chatapp-image
   ```