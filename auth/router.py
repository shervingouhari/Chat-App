from fastapi import APIRouter

from .utils import RequestForm, MongoDB, authenticate, create_access_token
from .schemas import Token


router = APIRouter()


@router.post(
    "/",
    response_description="Operation successful.",
    description="Returns a JWT if the given credentials are correct.",
    summary="Login"
)
async def login(
    user: RequestForm,
    db: MongoDB
) -> Token:
    user = await authenticate(user, db)
    access_token = create_access_token({"username": user["username"], "email": user["email"]})
    return Token(access_token=access_token)
