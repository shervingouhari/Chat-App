from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal, Callable
from functools import wraps

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import ValidationError
import jwt

from core.settings import MONGODB_COLLECTION_USERS, LOGIN_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRY
from core.mongodb import Manager
from core.exceptions import AuthenticationFailedError, ActionForbiddenError
from core.hash import is_valid_password
from .schemas import TokenPayload


collection = MONGODB_COLLECTION_USERS
OAuth2Scheme = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl=LOGIN_URL))]
RequestForm = Annotated[OAuth2PasswordRequestForm, Depends()]


async def authenticate(user_1: RequestForm) -> dict:
    user_2 = await Manager.get_or_fail(collection, {"username": user_1.username}, AuthenticationFailedError)
    if not is_valid_password(user_1.password, user_2["password"]):
        raise AuthenticationFailedError
    else:
        return user_2


def create_access_token(user: dict) -> str:
    exp = datetime.now(timezone.utc) + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRY)
    user.update({"exp": exp})
    return jwt.encode(user, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verified_access_token(token: str) -> dict:
    try:
        token = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            verify=True
        )
    except jwt.InvalidTokenError:
        raise AuthenticationFailedError

    try:
        return TokenPayload(
            username=token.get("username"),
            email=token.get("email")
        ).model_dump()
    except ValidationError:
        raise AuthenticationFailedError


def ensure_authority(mode: Literal["normal", "admin"]) -> Callable:
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
