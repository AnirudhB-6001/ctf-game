import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from database import init_db, db
import config
import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logging
logging.basicConfig(
    filename='ctf_game.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Rate limiter with Redis
    redis_client = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
    limiter = Limiter(get_remote_address, storage_uri=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/0", app=app, default_limits=["100 per hour"])
    
    # Flask Configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    
    init_db(app)
    jwt = JWTManager(app)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_blacklisted(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return redis_client.get(jti) == "blacklisted"
    
    with app.app_context():
        from routes.auth import create_auth_blueprint
        from routes.challenges import create_challenges_blueprint
        
        app.register_blueprint(create_auth_blueprint(limiter), url_prefix="/api/auth")
        app.register_blueprint(create_challenges_blueprint(limiter), url_prefix="/api/challenges")
        
    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        logging.info("CTF Game API started.")
    app.run(debug=True)
