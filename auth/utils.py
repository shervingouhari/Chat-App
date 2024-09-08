from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal
from functools import wraps

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
import jwt

from core.settings import MONGODB_COLLECTION_USERS, LOGIN_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRY
from core.database_utils import get_or_fail
from core.database import ConnectionManager
from core.exceptions import AuthenticationFailedError, ActionForbiddenError
from core.hash import is_valid_password


collection = MONGODB_COLLECTION_USERS
OAuth2Scheme = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl=LOGIN_URL))]
MongoDB = Annotated[AsyncIOMotorDatabase, Depends(ConnectionManager.get_db)]
RequestForm = Annotated[OAuth2PasswordRequestForm, Depends()]


async def authenticate(user_1: RequestForm, db: AsyncIOMotorDatabase) -> dict:
    user_2 = await get_or_fail(collection, {"username": user_1.username}, db, AuthenticationFailedError)
    if not is_valid_password(user_1.password, user_2["password"]):
        raise AuthenticationFailedError
    else:
        return user_2


def create_access_token(user: dict) -> str:
    exp = datetime.now(timezone.utc) + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRY)
    user.update({"exp": exp})
    return jwt.encode(user, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def ensure_authority(mode: Literal["normal", "admin"]):
    """
    Make sure the route parameter responsible for getting the user is named `user`.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            _id = str(kwargs.get("user")["_id"])
            object_id = str(kwargs.get("object_id"))
            is_admin = bool(kwargs.get("user").get("is_admin", False))
            if (
                (mode == "normal" and _id != object_id) or
                (mode == "admin" and not is_admin)
            ):
                raise ActionForbiddenError
            else:
                return await func(*args, **kwargs)
        return wrapper
    return decorator
