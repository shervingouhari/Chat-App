from pydantic import BaseModel

from core.settings import JWT_TOKEN_TYPE


class Token(BaseModel):
    access_token: str = ...
    token_type: str = JWT_TOKEN_TYPE
