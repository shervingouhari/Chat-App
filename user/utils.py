from typing import Annotated

from fastapi import Path, Body, Depends

from core.settings import MONGODB_COLLECTION_USERS
from auth.dependencies import get_user
from .schemas import UserCreate, UserUpdate, ReadUsersQP


collection = MONGODB_COLLECTION_USERS
ObjectID = Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$", description="The unique identifier of the user.")]
User = Annotated[dict, Depends(get_user)]
UserCreate = Annotated[UserCreate, Body(...)]
UserUpdate = Annotated[UserUpdate, Body(...)]
ReadUsersQP = Annotated[ReadUsersQP, Depends()]
