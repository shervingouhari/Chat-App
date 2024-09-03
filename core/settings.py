from pathlib import Path
import logging

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
LOG_LEVEL = logging.DEBUG


class Env(BaseSettings):
    MONGODB_URL: str = ...

    model_config = ConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
    )


env = Env()


API_PREFIX = "api"
ROUTER_DIRS = [
    "user",
    "auth",
]

MONGODB_URL = env.MONGODB_URL
MONGODB_DATABASE_NAME = "chat-app"
MONGODB_MAX_POOL_SIZE = 1
MONGODB_MIN_POOL_SIZE = 1

FAST_API_TITLE = "Chat App"
FAST_API_VERSION = "0.0.0"
FAST_API_DEBUG = False

UVICORN_NAME = "manage:app"
UVICORN_HOST = "127.0.0.1"
UVICORN_PORT = 5000
UVICORN_RELOAD = True
