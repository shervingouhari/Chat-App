from typing import Annotated
from functools import wraps

from fastapi import Path, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import ConnectionManager
from core.exceptions import ActionForbiddenError
from core.settings import USERS_COLLECTION
from auth.dependencies import get_user
from .schemas import UserCreate, UserUpdate, ReadUsersQP


collection = USERS_COLLECTION
ObjectID = Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$", description="The unique identifier of the user.")]
MongoDB = Annotated[AsyncIOMotorDatabase, Depends(ConnectionManager.get_db)]
User = Annotated[dict, Depends(get_user)]
UserCreate = Annotated[UserCreate, Body(...)]
UserUpdate = Annotated[UserUpdate, Body(...)]
ReadUsersQP = Annotated[ReadUsersQP, Depends()]


def ensure_authority(mode="normal"):
    """
    Make sure the route parameter responsible for getting the user is named `user`.
    Options are `normal` and `admin`.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if (
                (mode == "normal" and str(user["_id"]) != kwargs.get("object_id")) or
                (mode == "admin" and not bool(user.get("is_admin")))
            ):
                raise ActionForbiddenError
            else:
                return await func(*args, **kwargs)
        return wrapper
    return decorator
