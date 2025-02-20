import logging
import redis
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from models.user import User
from database import db
import bcrypt
import config
from functools import wraps

def create_auth_blueprint(limiter):
    bp = Blueprint("auth", __name__)

    # Connect to Redis
    redis_client = redis.StrictRedis(
        host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True
    )

    def role_required(required_role):
        def wrapper(fn):
            @wraps(fn)
            @jwt_required()
            def decorator(*args, **kwargs):
                claims = get_jwt()
                if "role" not in claims:
                    logging.warning(f"Access Denied: No role found for user {get_jwt_identity()}")
                    return jsonify({"error": "Access forbidden: No role found in token"}), 403
                if claims["role"] != required_role:
                    logging.warning(f"Unauthorized Role Access Attempt: {get_jwt_identity()} tried to access {required_role} route.")
                    return jsonify({"error": "Access forbidden: Insufficient role"}), 403
                return fn(*args, **kwargs)
            return decorator
        return wrapper

    @bp.route("/logout", methods=["POST"])
    @jwt_required()
    def logout():
        jti = get_jwt()["jti"]  # Get unique token identifier (JWT ID)
        redis_client.setex(jti, 3600, "blacklisted")  # Store token in Redis for 1 hour
        logging.info(f"User {get_jwt_identity()} logged out successfully.")
        return jsonify({"message": "Successfully logged out"}), 200

    @bp.route("/register", methods=["POST"])
    def register():
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            logging.warning(f"Failed Registration Attempt: Username {username} already exists.")
            return jsonify({"error": "User already exists"}), 409

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        new_user = User(username=username, password_hash=hashed_password, role="user")
        db.session.add(new_user)
        db.session.commit()

        logging.info(f"New User Registered: {username}")
        return jsonify({"message": "User registered successfully"}), 201

    @bp.route("/login", methods=["POST"])
    @limiter.limit("5 per minute")  # Limit login attempts
    def login():
        data = request.json
        username = data.get("username")
        password = data.get("password").encode("utf-8")

        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.checkpw(password, user.password_hash):
            logging.warning(f"Failed Login Attempt: Username {username}")
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        refresh_token = create_refresh_token(identity=str(user.id))

        logging.info(f"User Logged In: {username}")
        return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200

    @bp.route("/refresh", methods=["POST"])
    @jwt_required(refresh=True)
    def refresh():
        user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=str(user_id))
        logging.info(f"Token Refreshed for User ID {user_id}")
        return jsonify({"access_token": new_access_token}), 200

    return bp
