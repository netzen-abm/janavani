from flask import Flask, request, jsonify

# reuse your existing system
from src.conversation.engine import handle_message

app = Flask(__name__)

# simple session memory (temporary)
sessions = {}

@app.route("/")
def home():
    return "Janavani Web App Running"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    user_id = data.get("user_id", "web_user")
    message = data.get("message", "")

    if user_id not in sessions:
        sessions[user_id] = {}

    state = sessions[user_id]

    response = handle_message(message, state)

    return jsonify({
        "response": response,
        "state": state
    })


if __name__ == "__main__":
    app.run(debug=True)
