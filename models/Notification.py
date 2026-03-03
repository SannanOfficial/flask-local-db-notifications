from marshmallow import Schema, fields
from .db import db


class NotificationSchema(Schema):
    notification_type = fields.String(required=True)
    notification_for = fields.String(required=True)
    notification_redirect = fields.String(required=False)
    notification_created_at = fields.Number(required=False)


collection = db.notifications
