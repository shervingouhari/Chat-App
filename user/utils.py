from typing import Annotated, Optional
from enum import Enum

from fastapi import Path, Query
from pymongo import ASCENDING, DESCENDING
from pydantic import BaseModel, field_validator


ObjectID = Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$", description="The unique identifier of the user.")]


class OrderBy(Enum):
    object_id = "object_id"
    username = "username"
    email = "email"


class OrderDirection(Enum):
    ascending = "ascending"
    descending = "descending"


class ReadUsersQP(BaseModel):
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
        return DESCENDING if value == OrderDirection.descending else ASCENDING

    @field_validator('order_by', mode='after')
    def convert_order_by(cls, value):
        return "_id" if value == OrderBy.object_id else value.value
