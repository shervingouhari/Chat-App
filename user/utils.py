from typing import Annotated

from fastapi import Path, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import MongoDBConnectionManager
from core.settings import MONGODB_COLLECTION_USERS
from auth.dependencies import get_user
from .schemas import UserCreate, UserUpdate, ReadUsersQP


collection = MONGODB_COLLECTION_USERS
ObjectID = Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$", description="The unique identifier of the user.")]
MongoDB = Annotated[AsyncIOMotorDatabase, Depends(MongoDBConnectionManager.get_db)]
User = Annotated[dict, Depends(get_user)]
UserCreate = Annotated[UserCreate, Body(...)]
UserUpdate = Annotated[UserUpdate, Body(...)]
ReadUsersQP = Annotated[ReadUsersQP, Depends()]
