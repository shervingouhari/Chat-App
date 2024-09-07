from typing import Literal

from pydantic import BaseModel, Field

from core.settings import JWT_TOKEN_TYPE


class Token(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(JWT_TOKEN_TYPE)


class TokenPayload(BaseModel):
    username: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)


class AuthorityMode(BaseModel):
    mode: Literal["normal", "admin"] = Field(...)
