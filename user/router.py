from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import bson

from core.dependencies import get_db
from core.database_utils import get_or_fail, get_all_or_fail, create_or_fail, update_or_fail, delete_or_fail
from .models import UserCreate, UserUpdate, UserResponse, UsersResponse
from .utils import ReadUsersQP, ObjectID


router = APIRouter()
collection = "users"


@router.get(
    "/",
    response_model=UsersResponse,
    response_model_by_alias=False,
    response_description="Operation successful.",
    description="Returns the users matching the given query params from the database.",
    summary="Read Users"
)
async def read_users(
    qp: Annotated[ReadUsersQP, Depends()],
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    return UsersResponse(users=await get_all_or_fail(collection, qp, db))


@router.get(
    "/{object_id}",
    response_model=UserResponse,
    response_model_by_alias=False,
    response_description="Operation successful.",
    description="Returns the user with the given object_id from the database.",
    summary="Read User"
)
async def read_user(
    object_id: ObjectID,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    return await get_or_fail(collection, {"_id": bson.ObjectId(object_id)}, db)


@router.post(
    "/",
    response_model=UserResponse,
    response_model_by_alias=False,
    response_description="Operation successful.",
    description="Creates a user and returns the user object.",
    summary="Create User",
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    new_user = await create_or_fail(collection, user.model_dump(), db)
    created_user = await get_or_fail(collection, {"_id": bson.ObjectId(new_user.inserted_id)}, db)
    return created_user


@router.put(
    "/{object_id}",
    response_model=UserResponse,
    response_model_by_alias=False,
    response_description="Operation successful.",
    description="Updates the user with the given object_id and returns the user object.",
    summary="Update User"
)
async def update_user(
    object_id: ObjectID,
    user: UserUpdate = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user = user.model_dump()
    if len(user) < 1:
        return await get_or_fail(collection, {"_id": bson.ObjectId(object_id)}, db)
    else:
        return await update_or_fail(collection, object_id, user, db)


@router.delete(
    "/{object_id}",
    response_description="Operation successful.",
    summary="Delete User",
    description="Deletes the user with the given object_id.",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    object_id: ObjectID,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    await delete_or_fail(collection, object_id, db)
