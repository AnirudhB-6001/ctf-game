from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database import db
from models.challenge import Challenge

def create_challenges_blueprint(limiter):
    bp = Blueprint("challenges", __name__)

    @bp.route("/", methods=["GET"])
    def get_challenges():
        challenges = Challenge.query.all()
        return jsonify([{"id": c.id, "name": c.name, "difficulty": c.difficulty} for c in challenges])

    @bp.route("/add", methods=["POST"])
    @jwt_required()
    @limiter.limit("10 per minute")  # Prevents excessive challenge additions
    def add_challenge():
        data = request.json
        name = data.get("name")
        difficulty = data.get("difficulty")

        if not name or not difficulty:
            return jsonify({"error": "Name and difficulty are required"}), 400

        challenge = Challenge(name=name, difficulty=difficulty)
        db.session.add(challenge)
        db.session.commit()

        return jsonify({"message": "Challenge added successfully"}), 201

    return bp
