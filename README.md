# Real-Time Notifications Demo

A minimal, self-contained demo of a real-time notification system built with **Flask-SocketIO**, **MongoDB**, and a **pre/post middleware pipeline** (Similar to what is found in mongoose with node.js). When a notification is created, it flows through insert middlewares that timestamp it, persist it, generate a secure one-time data token, and push it to the correct connected client over WebSockets -- all in real time.

## Architecture

```
POST /send
  |
  v
send_notification(user_id)
  |
  v
insert_one_with_middleware(data)
  |
  +---> pre_middleware   : adds notification_created_at timestamp
  +---> MongoDB insert   : persists the notification document
  +---> post_middleware  : creates a NotificationDataToken,
  |                        signs a JWT around it, and emits
  |                        a 'generate' event to the WebSocket
  |                        server via an internal async client
  v
Notifications namespace (on_generate)
  |
  +---> verifies the data token JWT
  +---> looks up the notification record
  +---> finds the connected client whose JWT matches
  |     notification_for
  +---> emits 'new_notification' to that client's room
  v
Browser receives the event and renders it instantly
```

### File structure

```
test/
  app.py                              Flask + SocketIO server
  seed.py                             Seeds a demo user, prints JWT
  requirements.txt
  .env.example
  models/
    db.py                             Shared MongoClient
    Notification.py                   Notification schema + collection
    NotificationDataToken.py          One-time data token model
    User.py                           Minimal user model
    middlewares/
      pre/insert_one/Notification.py          Adds timestamp
      post/insert_one/Notification.py         Token + WS push
      functions/insert_one_with_middleware/
        Notification.py                       Composes pre -> insert -> post
  websockets/
    namespaces/Notifications.py       SocketIO namespace handling
                                      connect / generate / disconnect
  helpers/
    verify_jwt.py                     Verifies a user JWT against the DB
    notifications/
      send_notification.py            High-level "send a notification" function
      verify_notification_data_token.py  Validates a one-time data token
  templates/
    index.html                        Browser test client
```

## Prerequisites

- **Python 3.9+**
- **MongoDB** running locally (default `mongodb://localhost:27017`)

## Setup

```bash
cd test/

# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Edit .env and set a real JWT_SECRET_KEY (any random string works)

# 4. Seed a demo user
python seed.py
# This prints the user ID and a JWT -- the web UI fetches its own
# JWT automatically, so you can ignore this unless you want to
# test with curl.

# 5. Start the server
python app.py
```

Open **http://localhost:5000** in your browser. You will see a minimal page with a **Send "Hi!"** button. Each click triggers the full middleware pipeline and a real-time WebSocket push.

## How it works

1. **Browser** connects to the `/notifications` WebSocket namespace with a JWT header.
2. The **Notifications** namespace verifies the JWT, loads any existing notifications from MongoDB, and sends them as `all_notifications`.
3. Clicking the button calls `POST /send`, which invokes `send_notification(user_id)`.
4. `send_notification` calls `insert_one_with_middleware`, which runs:
   - **Pre-middleware**: injects `notification_created_at`.
   - **MongoDB insert**: stores the notification document.
   - **Post-middleware**: creates a `NotificationDataToken`, signs a short-lived JWT around it, and emits a `generate` event via an internal async SocketIO client.
5. The server-side `on_generate` handler verifies the data-token JWT, looks up the notification, finds the matching connected client, marks the token as used, and emits `new_notification` to that client.
6. The browser receives `new_notification` and renders it in the live feed.

## Testing with curl

```bash
# Send a notification (the server picks the first user automatically)
curl -X POST http://localhost:5000/send \
     -H "Content-Type: application/json"
```

## License

MIT
