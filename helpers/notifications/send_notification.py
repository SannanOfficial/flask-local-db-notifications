from models.middlewares.functions.insert_one_with_middleware.Notification import (
    insert_one_with_middleware as insert_one_notification,
)
import time


def send_notification(user_id, notification_type="info", notification_redirect="/"):
    """
    Send a real-time notification to a specific user.
    The notification is inserted through the middleware chain
    which handles timestamping (pre) and WebSocket delivery (post).
    """
    insert_one_notification({
        "notification_type": notification_type,
        "notification_for": str(user_id),
        "notification_redirect": notification_redirect,
        "notification_created_at": time.time(),
    })
