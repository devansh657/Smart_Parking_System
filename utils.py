import jwt
import datetime
import bcrypt
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")

# Google Maps API Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("Missing Google Maps API Key. Check your .env file!")


def generate_token(user_id):
    """Generate JWT token for authentication"""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def verify_token(token):
    """Verify JWT token and return decoded payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def hash_password(password):
    """Hash a password before storing in the database"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(password, hashed_password):
    """Check if the provided password matches the hashed password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_coordinates(location):
    """Fetch latitude and longitude using Google Maps API"""
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            print("Google Maps API Error:", response.json())
            return None

        data = response.json()

        if not data["results"]:
            print("No results from Google Maps API")
            return None

        coords = data["results"][0]["geometry"]["location"]
        return coords["lat"], coords["lng"]

    except Exception as e:
        print("Error in get_coordinates:", e)
        return None
