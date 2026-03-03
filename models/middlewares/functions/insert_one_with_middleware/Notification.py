from ...pre.insert_one.Notification import pre_middleware
from ...post.insert_one.Notification import post_middleware
from ....Notification import collection as collection


def insert_one_with_middleware(data):
    data = pre_middleware(data)
    result = collection.insert_one(data)
    return post_middleware(result.inserted_id)
