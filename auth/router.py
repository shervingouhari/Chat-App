from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.dependencies import get_db
from .utils import authenticate, create_access_token
from .schemas import Token


router = APIRouter()
collection = "users"


@router.post(
    "/",
    response_description="Operation successful.",
    description="Returns a JWT if the given credentials are correct.",
    summary="Login"
)
async def login(
    user: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Token:
    user = await authenticate(collection, user, db)
    access_token = create_access_token({"username": user["username"], "email": user["email"]})
    return Token(access_token=access_token)
