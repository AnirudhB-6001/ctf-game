from flask import Blueprint, jsonify

bp = Blueprint("challenges", __name__)

@bp.route("/", methods=["GET"])
def get_challenges():
    challenges = [
        {"id": 1, "name": "SQL Injection", "difficulty": "Easy"},
        {"id": 2, "name": "XSS Attack", "difficulty": "Medium"},
        {"id": 3, "name": "Buffer Overflow", "difficulty": "Hard"}
    ]
    return jsonify(challenges)