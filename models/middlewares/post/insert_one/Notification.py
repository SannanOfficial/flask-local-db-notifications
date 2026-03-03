from ....NotificationDataToken import collection as notification_data_token_collection
from dotenv import load_dotenv
import logging
import socketio
import asyncio
from threading import Thread
import jwt
from datetime import datetime, timedelta
from os import environ

load_dotenv()

logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
logging.basicConfig()

sio = socketio.AsyncClient(logger=True, engineio_logger=True)
event_loop = asyncio.new_event_loop()
task_queue = asyncio.Queue()


async def websocket_handler():
    try:
        await sio.connect(
            environ.get("SERVER_URL") + "?server_key=" +
            environ.get("SERVER_SECRET_KEY"),
            namespaces=['/notifications']
        )
        await sio.wait()
    except Exception as e:
        print(f"WebSocket connection failed: {e}")


async def process_tasks():
    while True:
        task = await task_queue.get()
        if task is None:
            break
        await task()


def start_event_loop():
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(websocket_handler())
    event_loop.run_until_complete(process_tasks())


thread = Thread(target=start_event_loop, daemon=True)
thread.start()


def create_custom_jwt(payload, secret_key, algorithm='HS256'):
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload['exp'] = expiration
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def post_middleware(result):
    notification_data_token_insert = notification_data_token_collection.insert_one({
        "notification_id": result,
        "used": False,
    })

    if notification_data_token_insert:
        notification_data_token = notification_data_token_collection.find_one({
            "_id": notification_data_token_insert.inserted_id
        })

        if notification_data_token:
            access_token = create_custom_jwt(
                {"sub": str(notification_data_token_insert.inserted_id)},
                environ.get("JWT_SECRET_KEY")
            )

            async def task():
                await sio.emit(
                    'generate',
                    data={"notificationtoken": access_token},
                    namespace='/notifications'
                )

            asyncio.run_coroutine_threadsafe(task(), event_loop)

            return {"status": "success", "data": result}
