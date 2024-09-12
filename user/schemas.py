from typing import Annotated, Optional, Literal, List, ClassVar
from abc import ABC

from fastapi import Query
from pymongo import ASCENDING, DESCENDING
from pydantic import BaseModel, ConfigDict, Field, EmailStr, SecretStr, BeforeValidator, field_validator, model_validator

from core.hash import hash_password as hp
from core.mongodb import Migration


username_field = {
    'min_length': 5,
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

    @field_validator('*', mode='after')
    def ensure_no_spaces(cls, value):
        if ' ' in (value.get_secret_value() if isinstance(value, SecretStr) else value):
            raise ValueError('Fields must not contain spaces.')
        return value

    @model_validator(mode='after')
    def hash_password(cls, items):
        if items.password is not None:
            items.password = hp(items.password.get_secret_value())
        return items


class UserCreate(BaseUser):
    username: str = Field(..., **username_field)
    email: EmailStr = Field(...)
    password: SecretStr = Field(..., **password_field)


class UserUpdate(BaseUser):
    username: Optional[str] = Field(None, **username_field)
    email: Optional[EmailStr] = Field(None)
    password: Optional[SecretStr] = Field(None, **password_field)

    def absolute_model_dump(self, *args, **kwargs) -> dict:
        original_dump = super().model_dump(*args, **kwargs)
        return {k: v for k, v in original_dump.items() if v is not None}


class UserResponse(BaseModel):
    object_id: Annotated[str, BeforeValidator(lambda object_id: str(object_id))] = Field(alias="_id")
    username: str
    email: str


class UsersResponse(BaseModel):
    users: List[UserResponse]


class ReadUsersQP(BaseModel):
    order_by: Literal["object_id", "username", "email"] = Query(
        "username", description="Field to order the results by"
    )
    order_direction: Literal["ascending", "descending"] = Query(
        "descending", description="Direction to order the results by"
    )
    skip: Optional[int] = Query(
        0, ge=0, description="Number of users to skip"
    )
    limit: Optional[int] = Query(
        10, ge=1, le=100, description="Number of users to return"
    )

    @field_validator('order_direction', mode='after')
    def convert_order_direction(cls, value):
        return DESCENDING if value == "descending" else ASCENDING

    @field_validator('order_by', mode='after')
    def convert_order_by(cls, value):
        return "_id" if value == "object_id" else value
