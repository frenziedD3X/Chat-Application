const BASE_URL = "https://chat-application-v5dw.onrender.com"; // Render Flask backend URL
let currentUser = null;
let currentChatUser = null;
let messagePollingInterval = null;  // To hold the polling interval reference

// Authentication Functions
async function register() {
  const name = document.getElementById("register-name").value;
  const email = document.getElementById("register-email").value;
  const password = document.getElementById("register-password").value;

  const response = await fetch(`${BASE_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  const result = await response.json();
  if (response.ok) {
    alert("Registered successfully! Please login.");
  } else {
    alert(result.error);
  }
}

async function login() {
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  const response = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const result = await response.json();
  if (response.ok) {
    currentUser = result.user_id;
    document.getElementById("auth-container").style.display = "none";
    document.getElementById("chat-container").style.display = "block";
    
    // Show the user's name instead of the email
    document.getElementById("current-user").innerText = result.user_name;

    // Fetch the list of users the current user has chatted with
    fetchConversations();
  } else {
    alert(result.error);
  }
}


async function logout() {
  // Clear the polling interval when logging out
  if (messagePollingInterval) {
    clearInterval(messagePollingInterval);
  }

  await fetch(`${BASE_URL}/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: currentUser }),
  });
  currentUser = null;
  currentChatUser = null;
  document.getElementById("auth-container").style.display = "block";
  document.getElementById("chat-container").style.display = "none";
}

// Chat Functions
async function searchUsers() {
  const query = document.getElementById("search-query").value;
  const response = await fetch(`${BASE_URL}/search?query=${query}`);
  const users = await response.json();
  const resultsList = document.getElementById("search-results");
  resultsList.innerHTML = "";
  users.forEach(user => {
    const li = document.createElement("li");
    li.textContent = `${user.name} `;
    li.onclick = () => selectUser(user.user_id, user.name);
    resultsList.appendChild(li);
  });
}

function selectUser(userId, userName) {
  currentChatUser = userId;
  document.getElementById("chat-title").innerText = `Chat with ${userName}`;
  fetchMessages();

  // Start polling for new messages every 5 seconds
  if (messagePollingInterval) {
    clearInterval(messagePollingInterval); // Clear any existing interval
  }
  messagePollingInterval = setInterval(fetchMessages, 2000); // Poll every 2 seconds
}

async function sendMessage() {
  const messageBox = document.getElementById("message-box");
  const message = messageBox.value;
  if (!message || !currentChatUser) return;

  await fetch(`${BASE_URL}/send_message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sender_id: currentUser,
      receiver_id: currentChatUser,
      message,
    }),
  });
  messageBox.value = "";
  fetchMessages();  // Immediately refresh the message list after sending a message
}

async function fetchMessages() {
  const response = await fetch(
    `${BASE_URL}/get_messages?sender_id=${currentUser}&receiver_id=${currentChatUser}`
  );
  const messages = await response.json();
  const messagesDiv = document.getElementById("messages");
  messagesDiv.innerHTML = ""; // Clear current messages

  // Loop through the messages and display them
  messages.forEach(msg => {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${msg.sender_id === currentUser ? "self" : ""}`;
    messageDiv.textContent = msg.message;
    messagesDiv.appendChild(messageDiv);
  });

  // Scroll to the bottom of the chat
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Fetch the users the current user has chatted with
async function fetchConversations() {
  const response = await fetch(`${BASE_URL}/get_conversations?user_id=${currentUser}`);
  const result = await response.json();
  const conversationsList = document.getElementById("conversations-list");

  // Clear current list
  conversationsList.innerHTML = "";

  // Add each user to the list with their name instead of user ID
  result.conversation_users.forEach(user => {
    const li = document.createElement("li");
    li.textContent = `User: ${user.name}`;  // Display user's name
    li.onclick = () => selectUser(user.user_id, user.name); // Pass user_id and name to the selectUser function
    conversationsList.appendChild(li);
  });
}

