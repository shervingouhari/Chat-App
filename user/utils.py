from typing import Annotated

from fastapi import Path, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.dependencies import get_db
from .schemas import UserCreate, UserUpdate, ReadUsersQP


ObjectID = Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$", description="The unique identifier of the user.")]
MongoDB = Annotated[AsyncIOMotorDatabase, Depends(get_db)]
UserCreate = Annotated[UserCreate, Body(...)]
UserUpdate = Annotated[UserUpdate, Body(...)]
ReadUsersQP = Annotated[ReadUsersQP, Depends()]
