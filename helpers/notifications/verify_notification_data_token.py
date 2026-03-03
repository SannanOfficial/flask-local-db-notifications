from bson.objectid import ObjectId
from flask_jwt_extended import decode_token
from models.Notification import collection as notification_collection
from models.NotificationDataToken import collection as notification_data_token_collection


def verify_notification_data_token(jwt):
    notification_data_token_id = decode_token(jwt, allow_expired=False)["sub"]

    if ObjectId.is_valid(notification_data_token_id) is False:
        return False

    notification_data_token_record = notification_data_token_collection.find_one(
        {"_id": ObjectId(notification_data_token_id), "used": False})

    if notification_data_token_record is None:
        return False

    notification_record = notification_collection.find_one(
        {"_id": ObjectId(notification_data_token_record["notification_id"])})

    if notification_record is None:
        return False

    return True
