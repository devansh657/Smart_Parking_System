import os
import joblib
import numpy as np
from flask import Blueprint, request, jsonify
from utils import get_coordinates
import requests
from config import Config

parking_routes = Blueprint('parking_routes', __name__)

# Load AI Model
MODEL_PATH = os.getenv("MODEL_PATH", "C:/Users/dmodi/Desktop/finalProject/model/best_parking_predictor_model.pkl")
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ AI model loaded successfully")
else:
    raise FileNotFoundError("❌ Model file not found at specified path!")

def get_nearby_parking(latitude, longitude):
    """Get nearby parking locations from Google Places API."""
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1500&type=parking&key={Config.GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and "results" in data:
        return [
            {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating", "No rating"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"]
            }
            for place in data["results"]
        ]
    return None

@parking_routes.route('/get_parking_slots', methods=['POST'])
def get_parking_slots():
    data = request.json
    location = data.get('location')
    postcode = data.get('postcode')

    if not location or not postcode:
        return jsonify({"error": "Location and postcode are required"}), 400

    coordinates = get_coordinates(f"{location}, {postcode}")

    if not coordinates:
        return jsonify({"error": "Failed to get location coordinates"}), 500

    latitude, longitude = coordinates
    parking_spots = get_nearby_parking(latitude, longitude)

    if not parking_spots:
        return jsonify({"error": "No parking spots found nearby"}), 404

    return jsonify({"parking_spots": parking_spots})

@parking_routes.route('/predict_parking_availability', methods=['POST'])
def predict_parking_availability():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    day_of_week = data.get("day_of_week")
    hour_of_day = data.get("hour_of_day")
    weather = data.get("weather")

    if None in [latitude, longitude, day_of_week, hour_of_day, weather]:
        return jsonify({"error": "All fields are required"}), 400

    input_data = np.array([[latitude, longitude, day_of_week, hour_of_day, weather]])
    prediction = model.predict(input_data)[0]
    availability = "Available" if prediction == 1 else "Not Available"

    return jsonify({"prediction": availability})
