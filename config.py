import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("Missing Google Maps API Key. Check your .env file!")
