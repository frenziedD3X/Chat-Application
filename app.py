from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Get the Firebase config from the environment variable
firebase_config_json = os.getenv('FIREBASE_CONFIG')
if firebase_config_json:
    firebase_config = json.loads(firebase_config_json)
else:
    raise ValueError("FIREBASE_CONFIG environment variable is not set")

# Initialize Firebase Admin SDK with the parsed config
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Get API key from environment variables
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv('FIREBASE_API_KEY')}"




# Flask Routes

@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "Anonymous")
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(email=email, password=password)
        user_id = user.uid

        # Add user info to Firestore
        db.collection("users").document(user_id).set({
            "email": email,
            "name": name,
            "online": False,
            "last_seen": None
        })
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/login', methods=['POST'])
def login_user():
    """Login a user"""
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Prepare the data for the request to Firebase Authentication REST API
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        # Send the request to Firebase Authentication API
        response = requests.post(FIREBASE_AUTH_URL, json=payload)

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the response and retrieve the ID token
            response_data = response.json()
            id_token = response_data.get("idToken")
            user_id = response_data.get("localId")


            # Set the user as online
            user_ref = db.collection("users").document(user_id)
            user_ref.update({"online": True})

            # Retrieve user info from Firestore
            user_data = user_ref.get().to_dict()
            user_name = user_data.get("name", "Anonymous")  # Default name if none exists

            return jsonify({
                "message": "Login successful",
                "user_id": user_id,
                "user_name": user_name,
                "id_token": id_token
            }), 200
        else:
            # If authentication failed, return an error
            error_data = response.json()
            return jsonify({"error": error_data.get("error", {}).get("message", "Authentication failed")}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/logout', methods=['POST'])
def logout_user():
    """Logout a user"""
    data = request.json
    user_id = data.get("user_id")
    try:
        # Set the user as offline
        user_ref = db.collection("users").document(user_id)
        user_ref.update({"online": False, "last_seen": firestore.SERVER_TIMESTAMP})
        return jsonify({"message": "User logged out successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/search', methods=['GET'])
def search_users():
    """Search for users by name or email"""
    query = request.args.get("query", "").lower()
    users_ref = db.collection("users").stream()
    results = []
    for user in users_ref:
        user_data = user.to_dict()
        if query in user_data["email"].lower() or query in user_data["name"].lower():
            results.append({
                "user_id": user.id,
                "email": user_data["email"],
                "name": user_data["name"]
            })
        
        # Limit the results to 5 users
        if len(results) >= 5:
            break

    return jsonify(results), 200


@app.route('/send_message', methods=['POST'])
def send_message():
    """Send a message between two users"""
    data = request.json
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    message = data.get("message")
    if not all([sender_id, receiver_id, message]):
        return jsonify({"error": "Missing fields"}), 400

    chat_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
    message_data = {
        "sender_id": sender_id,
        "message": message,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "read": False
    }

    # Save message to Firestore
    db.collection("chats").document(chat_id).collection("messages").add(message_data)

    # Update chat metadata
    db.collection("chats").document(chat_id).set({
        "participants": [sender_id, receiver_id],
        "last_message": message,
        "last_message_time": firestore.SERVER_TIMESTAMP
    }, merge=True)

    return jsonify({"message": "Message sent successfully"}), 200


@app.route('/get_messages', methods=['GET'])
def get_messages():
    """Retrieve messages for a specific chat"""
    sender_id = request.args.get("sender_id")
    receiver_id = request.args.get("receiver_id")
    if not all([sender_id, receiver_id]):
        return jsonify({"error": "Missing fields"}), 400

    chat_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
    messages_ref = db.collection("chats").document(chat_id).collection("messages").order_by("timestamp").stream()

    messages = [{"message_id": msg.id, **msg.to_dict()} for msg in messages_ref]
    return jsonify(messages), 200

@app.route('/get_conversations', methods=['GET'])
def get_conversations():
    """Retrieve users the current user has messaged, returning their names"""
    current_user_id = request.args.get("user_id")
    if not current_user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Find all chats where the current user is a participant
    chats_ref = db.collection("chats").where("participants", "array_contains", current_user_id).stream()

    # Collect all users the current user has messaged
    conversation_users = []
    for chat in chats_ref:
        chat_data = chat.to_dict()
        participants = chat_data.get("participants", [])
        # Exclude the current user from the participants list
        other_users = [user for user in participants if user != current_user_id]
        conversation_users.extend(other_users)

    # Remove duplicates (if any)
    unique_users = list(set(conversation_users))

    # Retrieve the names of the unique users
    users_data = []
    for user_id in unique_users:
        user_ref = db.collection("users").document(user_id).get()
        if user_ref.exists:
            user_data = user_ref.to_dict()
            users_data.append({
                "user_id": user_id,
                "name": user_data.get("name", "Unknown")  # Default to "Unknown" if name is missing
            })

    return jsonify({"conversation_users": users_data}), 200


if __name__ == '__main__':
    app.run(debug=True)
