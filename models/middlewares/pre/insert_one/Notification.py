import time


def pre_middleware(data):
    data["notification_created_at"] = time.time()
    return data
