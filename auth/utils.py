from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
import jwt

from core.settings import USERS_COLLECTION, LOGIN_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRY
from core.database_utils import get_or_fail
from core.database import ConnectionManager
from core.exceptions import AuthenticationFailedError
from core.hash import is_valid_password


collection = USERS_COLLECTION
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=LOGIN_URL)
OAuth2Scheme = Annotated[str, Depends(oauth2_scheme)]
MongoDB = Annotated[AsyncIOMotorDatabase, Depends(ConnectionManager.get_db)]
RequestForm = Annotated[OAuth2PasswordRequestForm, Depends()]


async def authenticate(user_1: OAuth2PasswordRequestForm, db: AsyncIOMotorDatabase) -> dict:
    user_2 = await get_or_fail(collection, {"username": user_1.username}, db, AuthenticationFailedError)
    if not is_valid_password(user_1.password, user_2["password"]):
        raise AuthenticationFailedError
    else:
        return user_2


def create_access_token(user: dict) -> str:
    exp = datetime.now(timezone.utc) + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRY)
    user.update({"exp": exp})
    return jwt.encode(user, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
