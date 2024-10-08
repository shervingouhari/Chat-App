from pathlib import Path
import logging

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
LOG_LEVEL = logging.DEBUG


class Env(BaseSettings):
    MONGODB_URL: str = ...
    REDIS_URL: str = ...
    JWT_SECRET_KEY: str = ...

    model_config = ConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra='allow',
    )


env = Env()


API_PREFIX = "api"
LOGIN_URL = f"/{API_PREFIX}/auth/"
ROUTER_DIRS = [
    "user",
    "auth",
]

FAST_API_TITLE = "Chat App"
FAST_API_VERSION = "0.0.0"
FAST_API_DEBUG = False

UVICORN_NAME = "manage:app"
UVICORN_HOST = "127.0.0.1"
UVICORN_PORT = 5000
UVICORN_RELOAD = True

MONGODB_URL = env.MONGODB_URL
MONGODB_MAX_POOL_SIZE = 1
MONGODB_MIN_POOL_SIZE = 1
MONGODB_DATABASE_NAME = "chat-app"
MONGODB_COLLECTION_USERS = "users"

REDIS_URL = env.REDIS_URL

SOCKETIO_PING_INTERVAL = 25
SOCKETIO_PING_TIMEOUT = 5
SOCKETIO_DEBUG = False
SOCKETIO_CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'https://admin.socket.io'
]

JWT_TOKEN_TYPE = "bearer"
JWT_ALGORITHM = "HS256"
JWT_SECRET_KEY = env.JWT_SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRY = 120 * 60
