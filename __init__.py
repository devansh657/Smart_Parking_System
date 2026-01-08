import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Secret Key for JWT
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.smart_parking

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Import and register blueprints
from routes import auth_routes, parking_routes

app.register_blueprint(auth_routes, url_prefix="/auth")
app.register_blueprint(parking_routes, url_prefix="/parking")

# Default route
@app.route("/")
def home():
    return {"message": "Smart Parking System API is running!"}

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
