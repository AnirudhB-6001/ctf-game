import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'ctf_game.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "supersecretkey"  # Change this in production
JWT_SECRET_KEY = "very_secure_jwt_secret_key"  # Change this for production
JWT_ACCESS_TOKEN_EXPIRES = 900  # Tokens expire in 15 minutes
JWT_REFRESH_TOKEN_EXPIRES = 86400  # 1 day
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0