from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "smart_parking")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
parking_collection = db["parking_slots"]

print("✅ Database connected successfully!")

# Optional: Define indexes for better query performance
users_collection.create_index("email", unique=True)
parking_collection.create_index([("location", "text")])
