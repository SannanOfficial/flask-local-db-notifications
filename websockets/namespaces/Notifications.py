from flask import request
from flask_socketio import Namespace, emit
from dotenv import load_dotenv
from helpers.notifications.verify_notification_data_token import verify_notification_data_token
from helpers.verify_jwt import verify_jwt
from models.NotificationDataToken import collection as notification_data_token_collection
from models.Notification import collection as notification_collection
from models.User import collection as user_collection
from bson.objectid import ObjectId
import json
from bson import json_util
import jwt
from os import environ
from pymongo import DESCENDING

load_dotenv()

clients = []


def decode_custom_jwt(token, secret_key, algorithm='HS256'):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
    except jwt.InvalidTokenError:
        print("Invalid token.")
    except Exception as e:
        print(f"Error decoding JWT: {e}")


class Notifications(Namespace):
    def on_connect(self):
        if request.headers.get("jwt") is not None:
            jwt = request.headers.get("jwt")

            if verify_jwt(jwt) is False:
                return False

            user_id = decode_custom_jwt(
                jwt, environ.get("JWT_SECRET_KEY"))["sub"]

            notifications = list(notification_collection.find(
                {"notification_for": user_id}).sort("notification_created_at", DESCENDING))

            emit("all_notifications", json.loads(
                json_util.dumps(notifications)))

            clients.append({
                "sid": request.sid,
                "headers": request.headers,
            })

    def on_generate(self, data):
        if request.headers.get("jwt") is not None:
            return False

        jwt = data["notificationtoken"]

        if jwt is None:
            return {"message": "No JWT provided."}
        else:
            if verify_notification_data_token(jwt) is not False:
                notification_data_token_id = decode_custom_jwt(
                    jwt, environ.get("JWT_SECRET_KEY"))["sub"]

                notification_data_token_record = notification_data_token_collection.find_one({
                    "_id": ObjectId(notification_data_token_id),
                    "used": False,
                })

                if notification_data_token_record is not None:
                    notification_record = notification_collection.find_one({
                        "_id": ObjectId(notification_data_token_record["notification_id"])
                    })

                    if notification_record is not None:
                        user_record = user_collection.find_one({
                            "_id": ObjectId(notification_record["notification_for"]),
                        })

                        if user_record is not None:
                            json_data = json.loads(
                                json_util.dumps(notification_record))

                            for client in clients:
                                if client["sid"] is not None:
                                    user_id = decode_custom_jwt(client["headers"].get(
                                        "jwt"), environ.get("JWT_SECRET_KEY"))["sub"]
                                    if user_id == notification_record["notification_for"]:
                                        emit("access_granted")
                                        notification_data_token_collection.find_one_and_update({
                                            "_id": ObjectId(notification_data_token_id),
                                            "used": False,
                                        }, {
                                            "$set": {
                                                "used": True,
                                            }
                                        })
                                        emit("new_notification", json_data,
                                             room=client["sid"], to=client["sid"])

    def on_disconnect(self):
        global clients
        for client in clients:
            if client["sid"] == request.sid:
                clients.remove(client)
                break
