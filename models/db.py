from pymongo import MongoClient
from os import environ
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(environ.get("MONGODB_URI"))
db = client[environ.get("MONGODB_DATABASE", "notifications_demo")]
