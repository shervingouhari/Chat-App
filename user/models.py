from typing import Annotated, Optional, List, ClassVar
from abc import ABC

from pydantic import BaseModel, Field, EmailStr, SecretStr, BeforeValidator, ConfigDict, model_validator
from pymongo import ASCENDING

from core.hash import hash_password as hp
from core.database import Migration


class BaseUser(BaseModel, Migration, ABC):
    collection: ClassVar = "users"
    unique: ClassVar = [("username", ASCENDING), ("email", ASCENDING)]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode='before')
    def no_spaces(cls, items):
        for value in items.values():
            if isinstance(value, str) and ' ' in value:
                raise ValueError('Fields must not contain spaces.')
        return items

    def model_dump(self, *args, **kwargs):
        original_dump = super().model_dump(*args, **kwargs)
        absolute_dump = {k: v for k, v in original_dump.items() if v is not None}
        if absolute_dump.get("password") is not None:
            absolute_dump["password"] = hp(self.password.get_secret_value())
        return absolute_dump


class UserCreate(BaseUser):
    username: str = Field(
        ...,
        mix_length=8,
        max_length=20,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )
    email: EmailStr = Field(...)
    password: SecretStr = Field(..., min_length=8, max_length=20)


class UserUpdate(BaseUser):
    username: Optional[str] = Field(
        None,
        mix_length=8,
        max_length=20,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )
    email: Optional[EmailStr] = Field(None)
    password: Optional[SecretStr] = Field(None, min_length=8, max_length=20)


class UserResponse(BaseModel):
    object_id: Annotated[
        str,
        BeforeValidator(lambda object_id: str(object_id))
    ] = Field(alias="_id")
    username: str
    email: str


class UsersResponse(BaseModel):
    users: List[UserResponse]
