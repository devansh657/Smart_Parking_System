import os
import requests
import joblib
import numpy as np
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Secret key for JWT authentication
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

# ✅ Google API Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("❌ Missing Google Maps API Key. Check your .env file!")

# ✅ Load AI Model
MODEL_PATH = os.path.join(os.getcwd(), "C:/Users/dmodi/Desktop/finalProject/model/best_parking_predictor_model.pkl")
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print(f"✅ AI model loaded successfully from {MODEL_PATH}")
else:
    raise FileNotFoundError(f"❌ Model file not found at {MODEL_PATH}")

# ✅ Import routes (After defining app)
from routes.auth_routes import auth_routes  
from routes.parking_routes import parking_routes

# ✅ Register Blueprints
app.register_blueprint(auth_routes, url_prefix="/auth")
app.register_blueprint(parking_routes, url_prefix="/parking")

# ✅ Initialize MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/parking_system"
mongo = PyMongo(app)

# ✅ Function to Get Nearby Parking Locations
def get_nearby_parking(latitude, longitude):
    try:
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1500&type=parking&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            print("❌ Google Places API Error:", response.json())
            return None

        data = response.json()
        if "results" not in data or not data["results"]:
            print("⚠️ No parking spots found")
            return None

        return [
            {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"]
            } 
            for place in data["results"]
        ]
    except Exception as e:
        print("❌ Error in get_nearby_parking:", e)
        return None

# ✅ AI Model Prediction Route
@app.route('/predict_parking_availability', methods=['POST'])
def predict_parking_availability():
    try:
        data = request.json
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        day_of_week = data.get("day_of_week")
        hour_of_day = data.get("hour_of_day")
        weather = data.get("weather")
        weather = weather.title()

        weather_dict = {'Clear':0,'Windy':1,'Snowy':2,'Rainy':3,'Cloudy':4,'Foggy':5,'Stormy':6}
        if weather in weather_dict:
            weather = weather_dict[weather]

        print(latitude, type(latitude))
        print(longitude, type(longitude))
        print(day_of_week, type(day_of_week))
        print(hour_of_day, type(hour_of_day))
        print(weather, type(weather))

        if None in [latitude, longitude, day_of_week, hour_of_day, weather]:
            return jsonify({"error": "All fields are required"}), 400

        parking_spots = get_nearby_parking(latitude, longitude)
        if not parking_spots:
            return jsonify({"error": "No nearby parking locations found"}), 404

        predictions = [
            {
                "name": spot["name"],
                "address": spot["address"],
                "lat": spot["lat"],
                "lng": spot["lng"],
                "availability": "Available" if model.predict(np.array([[spot["lat"], spot["lng"], day_of_week, weather, hour_of_day]]))[0] == 1 else "Not Available"
            }
            for spot in parking_spots
        ]

        return jsonify({"predicted_parking_spots": predictions})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

# ✅ Route to Get Parking Slots
@app.route('/get_parking_slots', methods=['POST'])
def get_parking_slots():
    try:
        data = request.json
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not latitude or not longitude:
            return jsonify({"error": "Latitude and longitude are required"}), 400

        parking_spots = get_nearby_parking(latitude, longitude)
        if not parking_spots:
            return jsonify({"error": "No nearby parking locations found"}), 404

        return jsonify({"parking_spots": parking_spots})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Route to Book a Slot
@app.route('/book_parking', methods=['POST'])
def book_parking():
    try:
        data = request.json
        # location_id = data.get("location_id")
        #spot_name = data.get('name'),
        #spot_address = data.get('address'),
        #spot_longitude = data.get('longitude'),
        #spot_latitude = data.get('latitude'),
        
        user_id = data.get("67d3276d26360c86d007935b")
        location_id = data.get("")
        
        print(data)

        if not location_id or not user_id:
            return jsonify({"error": "Location ID and User ID are required"}), 400

        # Find the parking lot by location_id
        parking_lot = mongo.db.parking_slots.find_one({"location_id": location_id})
        
        if not parking_lot:
            return jsonify({"error": "Parking lot not found"}), 404

        # Check if there's an available slot
        if parking_lot["available_slots"] <= 0:
            return jsonify({"error": "No available slots left"}), 400

        # Update the available slots and add the user to booked slots
        mongo.db.parking_slots.update_one(
            {"location_id": location_id},
            {
                "$inc": {"available_slots": -1},  # Decrease available slots by 1
                "$push": {"booked_slots": user_id}  # Add user to booked slots
            }
        )

        return jsonify({"message": "Slot booked successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Route to Cancel Booking
@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    try:
        data = request.json
        location_id = data.get("location_id")
        user_id = data.get("user_id")

        if not location_id or not user_id:
            return jsonify({"error": "Location ID and User ID are required"}), 400

        # Find the parking lot by location_id
        parking_lot = mongo.db.parking_slots.find_one({"location_id": location_id})
        
        if not parking_lot:
            return jsonify({"error": "Parking lot not found"}), 404

        # Check if the user has booked the slot
        if user_id not in parking_lot["booked_slots"]:
            return jsonify({"error": "User has not booked this slot"}), 400

        # Update the available slots and remove the user from booked slots
        mongo.db.parking_slots.update_one(
            {"location_id": location_id},
            {
                "$inc": {"available_slots": 1},  # Increase available slots by 1
                "$pull": {"booked_slots": user_id}  # Remove user from booked slots
            }
        )

        return jsonify({"message": "Booking canceled successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
