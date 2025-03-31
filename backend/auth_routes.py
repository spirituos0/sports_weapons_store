from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, unset_jwt_cookies
)
from backend.models import User
from backend import db  

auth_bp = Blueprint("auth", __name__)


# Registration
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not all(key in data for key in ("username", "email", "password")):
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])
    
    db.session.add(user)
    db.session.commit()

    # We create a token immediately after registration 
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "User registered successfully",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 201

# Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not all(key in data for key in ("username", "password")):
        return jsonify({"error": "Missing fields"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


# Token update (refresh) 
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity() # Get user_id from token
    new_access_token = create_refresh_token(identity=user_id)  # user_id is already a string
    return jsonify({"access_token": new_access_token})

# Logout
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)  # Removes JWT tokens from cookies
    return response, 200



@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role if hasattr(user, "role") else "User",
        "created_at": user.created_at.strftime("%Y-%m-%d") if hasattr(user, "created_at") else "Unknown",
        "balance": user.balance
    }), 200


@auth_bp.route('/profile/deposit', methods=['POST'])
@jwt_required()
def deposit_money():
    user_id = get_jwt_identity()
    data = request.get_json()
    amount = data.get("amount")

    if amount is None or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 422

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fixing the "NoneType + int" error
    if user.balance is None:
        user.balance = 0.0

    user.balance += amount  
    db.session.commit()

    return jsonify({"message": "Balance updated", "new_balance": user.balance}), 200