from bson.objectid import ObjectId
from flask_jwt_extended import decode_token
from models.User import collection as user


def verify_jwt(jwt):
    user_id = decode_token(jwt, allow_expired=False)["sub"]

    if ObjectId.is_valid(user_id) is False:
        return False

    user_record = user.find_one({"_id": ObjectId(user_id)})

    if user_record is None:
        return False

    return True
