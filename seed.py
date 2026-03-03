"""
Seed script: creates a test user in MongoDB and prints a JWT for use with the demo.
Run once before starting the server:
    python seed.py
"""
from pymongo import MongoClient
from dotenv import load_dotenv
from os import environ
from datetime import datetime, timedelta
import jwt

load_dotenv()

client = MongoClient(environ.get("MONGODB_URI"))
db = client[environ.get("MONGODB_DATABASE", "notifications_demo")]

# Upsert a single demo user
existing = db.users.find_one({"username": "demo"})
if existing:
    user_id = str(existing["_id"])
    print(f"Demo user already exists: {user_id}")
else:
    result = db.users.insert_one({"username": "demo"})
    user_id = str(result.inserted_id)
    print(f"Created demo user: {user_id}")

secret = environ.get("JWT_SECRET_KEY")
token = jwt.encode(
    {
        "sub": user_id,
        "fresh": False,
        "type": "access",
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),
        "jti": "seed-token",
        "exp": datetime.utcnow() + timedelta(weeks=52),
    },
    secret,
    algorithm="HS256",
)

print(f"\nJWT (copy this into the test page or use it as a header):\n{token}\n")
