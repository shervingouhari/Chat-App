from typing import Annotated

from fastapi import Path, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.dependencies import get_db
from auth.dependencies import get_user
from .schemas import UserCreate, UserUpdate, ReadUsersQP


collection = "users"
ObjectID = Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$", description="The unique identifier of the user.")]
MongoDB = Annotated[AsyncIOMotorDatabase, Depends(get_db)]
User = Annotated[dict, Depends(get_user)]
UserCreate = Annotated[UserCreate, Body(...)]
UserUpdate = Annotated[UserUpdate, Body(...)]
ReadUsersQP = Annotated[ReadUsersQP, Depends()]
