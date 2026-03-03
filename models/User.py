from marshmallow import Schema, fields
from .db import db


class UserSchema(Schema):
    username = fields.String(required=True)


collection = db.users
