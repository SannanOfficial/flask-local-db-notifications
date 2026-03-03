from marshmallow import Schema, fields
from .db import db


class NotificationDataTokenSchema(Schema):
    notification_id = fields.String(required=True)
    used = fields.Boolean(required=True)
    token_created_at = fields.Number(required=False)


collection = db.notificationdatatoken
