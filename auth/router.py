from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.dependencies import get_db
from core.database_utils import get_or_fail
from core.exceptions import AuthenticationFailedError
from core.hash import is_valid_password
from .schemas import AuthLogin


router = APIRouter()
collection = "users"


@router.post(
    "/",
    response_description="Operation successful.",
    description="Returns a JWT if the given credentials are correct.",
    summary="Login"
)
async def login(
    user: AuthLogin = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user_1 = user.model_dump()
    user_2 = await get_or_fail(collection, {"username": user_1["username"]}, db, AuthenticationFailedError)
    if is_valid_password(user_1["password"], user_2["password"]):
        return {"jwt": "token"}
    else:
        raise AuthenticationFailedError
