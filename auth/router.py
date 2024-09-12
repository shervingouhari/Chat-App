from fastapi import APIRouter

from .utils import RequestForm, authenticate, create_access_token
from .schemas import Token


router = APIRouter()


@router.post(
    "/",
    response_description="Operation successful.",
    description="Returns a JWT if the given credentials are correct.",
    summary="Login"
)
async def login(body: RequestForm) -> Token:
    user = await authenticate(body)
    access_token = create_access_token({"username": user["username"], "email": user["email"]})
    return Token(access_token=access_token)
