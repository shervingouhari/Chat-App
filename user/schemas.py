from typing import Annotated, Optional, List, ClassVar
from enum import Enum
from abc import ABC

from pydantic import BaseModel, ConfigDict, Field, EmailStr, SecretStr, BeforeValidator, model_validator, field_validator
from pymongo import ASCENDING, DESCENDING
from fastapi import Path, Query

from core.hash import hash_password as hp
from core.database import Migration


ObjectID = Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$", description="The unique identifier of the user.")]
username_field = {
    'min_length': 8,
    'max_length': 20,
    'pattern': r'^[a-zA-Z0-9_-]+$'
}
password_field = {
    'min_length': 8,
    'max_length': 20
}


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
    username: str = Field(..., **username_field)
    email: EmailStr = Field(...)
    password: SecretStr = Field(..., **password_field)


class UserUpdate(BaseUser):
    username: Optional[str] = Field(None, **username_field)
    email: Optional[EmailStr] = Field(None)
    password: Optional[SecretStr] = Field(None, **password_field)


class UserResponse(BaseModel):
    object_id: Annotated[str, BeforeValidator(lambda object_id: str(object_id))] = Field(alias="_id")
    username: str
    email: str


class UsersResponse(BaseModel):
    users: List[UserResponse]


class ReadUsersQP(BaseModel):
    class OrderBy(Enum):
        object_id = "object_id"
        username = "username"
        email = "email"

    class OrderDirection(Enum):
        ascending = "ascending"
        descending = "descending"

    order_by: OrderBy = Query(
        OrderBy.username, description="Field to order the results by"
    )
    order_direction: OrderDirection = Query(
        OrderDirection.descending, description="Direction to order the results by"
    )
    skip: Optional[int] = Query(
        0, ge=0, description="Number of users to skip"
    )
    limit: Optional[int] = Query(
        10, ge=1, le=100, description="Number of users to return"
    )

    @field_validator('order_direction', mode='after')
    def convert_order_direction(cls, value):
        return DESCENDING if value == cls.OrderDirection.descending else ASCENDING

    @field_validator('order_by', mode='after')
    def convert_order_by(cls, value):
        return "_id" if value == cls.OrderBy.object_id else value.value
