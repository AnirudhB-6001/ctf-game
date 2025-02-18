from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt
from routes import challenges, auth
from database import init_db, db
import config
import redis

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY

# Initialize database and JWT
init_db(app)
jwt = JWTManager(app)

# Connect to Redis
redis_client = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)

# Check if token is blacklisted
@jwt.token_in_blocklist_loader
def check_if_token_blacklisted(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return redis_client.get(jti) == "blacklisted"

app.register_blueprint(challenges.bp, url_prefix="/api/challenges")
app.register_blueprint(auth.bp, url_prefix="/api/auth")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
