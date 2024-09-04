from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database_utils import get_or_fail
from core.exceptions import AuthenticationFailedError
from core.hash import is_valid_password


async def authenticate(collection: str, user_1: dict, db: AsyncIOMotorDatabase) -> dict:
    user_2 = await get_or_fail(collection, {"username": user_1["username"]}, db, AuthenticationFailedError)
    if not is_valid_password(user_1["password"], user_2["password"]):
        raise AuthenticationFailedError
    else:
        return user_2
