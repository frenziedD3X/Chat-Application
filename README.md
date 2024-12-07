```markdown
# Flask Chat Application with Firebase

This is a simple chat application built using Flask, Firebase Authentication, and Firestore. It allows users to register, login, send messages, and manage their conversations. The application leverages Firebase for user authentication and Firestore for storing chat messages.

## Features

- **User Registration and Login**: Users can register and log in using email and password via Firebase Authentication.
- **Chat System**: Users can send messages to each other, and messages are stored in Firebase Firestore.
- **Search Users**: Users can search for other users by name or email.
- **Track User Status**: Users are marked as "online" or "offline," and their last seen time is tracked.
- **Retrieve Conversations**: Users can retrieve a list of people they have chatted with.

## Prerequisites

- Python 3.7+
- Flask
- Firebase Admin SDK
- Firebase Project with Firestore and Firebase Authentication enabled
- Environment variables for Firebase credentials

## Setup

### 1. Install Dependencies

You can install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Before running the app, you need to set the following environment variables. You can set them manually in your operating system or through a deployment platform (e.g., Heroku, Docker).

#### Required Environment Variables:

- **FIREBASE_CONFIG**: Firebase credentials in JSON format (as a string).
- **FIREBASE_API_KEY**: The Firebase Web API Key.

For example, on Linux/macOS:

```bash
export FIREBASE_CONFIG='{
    "type": "service_account",
    "project_id": "your_firebase_project_id",
    "private_key_id": "your_firebase_private_key_id",
    "private_key": "your_firebase_private_key",
    "client_email": "your_firebase_client_email",
    "client_id": "your_firebase_client_id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your_firebase_client_x509_cert_url"
}'

export FIREBASE_API_KEY="your_firebase_api_key"
```

On Windows, use `set` to define environment variables:

```cmd
set FIREBASE_CONFIG={"type":"service_account",...}
set FIREBASE_API_KEY=your_firebase_api_key
```

### 3. Running the Application

Once you have set the environment variables, run the Flask application with the following command:

```bash
python app.py
```

The Flask server will start, and you can access the application at `http://127.0.0.1:5000`.

## API Endpoints

### `/register` (POST)
Registers a new user.
- **Request Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "User registered successfully",
    "user_id": "uid_here"
  }
  ```

### `/login` (POST)
Logs in a user.
- **Request Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "Login successful",
    "user_id": "uid_here",
    "user_name": "John Doe",
    "id_token": "id_token_here"
  }
  ```

### `/logout` (POST)
Logs out a user and updates their status to "offline."
- **Request Body**: 
  ```json
  {
    "user_id": "uid_here"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "User logged out successfully"
  }
  ```

### `/search` (GET)
Searches for users by name or email.
- **Query Parameters**: `query` (search string).
- **Response**: 
  ```json
  [
    {
      "user_id": "uid_here",
      "email": "user@example.com",
      "name": "John Doe"
    }
  ]
  ```

### `/send_message` (POST)
Sends a message between two users.
- **Request Body**: 
  ```json
  {
    "sender_id": "uid_sender",
    "receiver_id": "uid_receiver",
    "message": "Hello, how are you?"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "Message sent successfully"
  }
  ```

### `/get_messages` (GET)
Retrieves messages between two users.
- **Query Parameters**: `sender_id`, `receiver_id`.
- **Response**: 
  ```json
  [
    {
      "message_id": "message_id",
      "sender_id": "uid_sender",
      "message": "Hello, how are you?",
      "timestamp": "timestamp_here",
      "read": false
    }
  ]
  ```

### `/get_conversations` (GET)
Retrieves users the current user has messaged, returning their names.
- **Query Parameters**: `user_id`.
- **Response**: 
  ```json
  {
    "conversation_users": [
      {
        "user_id": "uid_here",
        "name": "Jane Doe"
      }
    ]
  }
  ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

