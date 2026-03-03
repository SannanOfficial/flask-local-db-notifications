from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from os import environ
from datetime import datetime, timedelta
import jwt as pyjwt
from websockets.namespaces.Notifications import Notifications
from helpers.notifications.send_notification import send_notification
from models.User import collection as user_collection

load_dotenv()

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(weeks=52)
app.config["JWT_SECRET_KEY"] = environ.get("JWT_SECRET_KEY")

CORS(app, origins="*", supports_credentials=True)

socketio.on_namespace(Notifications("/notifications"))

jwt = JWTManager(app)


@app.route("/")
def index():
    user = user_collection.find_one()
    user_id = str(user["_id"]) if user else None

    return render_template("index.html", user_id=user_id)


@app.route("/jwt")
def get_jwt():
    user = user_collection.find_one()
    if not user:
        return jsonify({"error": "No users found. Run seed.py first."}), 400

    user_id = str(user["_id"])
    secret = environ.get("JWT_SECRET_KEY")
    token = pyjwt.encode(
        {
            "sub": user_id,
            "fresh": False,
            "type": "access",
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow(),
            "jti": "auto-token",
            "exp": datetime.utcnow() + timedelta(weeks=52),
        },
        secret,
        algorithm="HS256",
    )

    return jsonify({"token": token, "user_id": user_id})


@app.route("/send", methods=["POST"])
def send():
    """Trigger a 'Hi!' notification to a user."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if not user_id:
        # Default: send to the first user in the DB
        user = user_collection.find_one()
        if not user:
            return jsonify({"error": "No users found. Run seed.py first."}), 400
        user_id = str(user["_id"])

    send_notification(
        user_id=user_id,
        notification_type="info",
        notification_redirect="/",
    )

    return jsonify({"status": "sent", "to": user_id})


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
