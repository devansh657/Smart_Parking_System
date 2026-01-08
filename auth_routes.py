from flask import Blueprint, request, jsonify
import jwt
import datetime
import os
from flask_bcrypt import Bcrypt
from models import users_collection  # Import database collection

auth_routes = Blueprint("auth_routes", __name__)
bcrypt = Bcrypt()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = users_collection.find_one({"email": email})

        # ✅ If the user does not exist, automatically register them
        if not user:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            users_collection.insert_one({"email": email, "password": hashed_password})
            user = users_collection.find_one({"email": email})  # Fetch the new user

        # ✅ Check password
        if not bcrypt.check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        # ✅ Generate JWT token
        token = jwt.encode(
            {"email": email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
            SECRET_KEY, algorithm="HS256"
        )

        return jsonify({"message": "Login successful", "token": token}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
