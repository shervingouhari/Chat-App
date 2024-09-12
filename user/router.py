from fastapi import APIRouter, status
import bson

from core.mongodb import Manager
from auth.utils import ensure_authority
from .schemas import UserResponse, UsersResponse
from .utils import collection, ObjectID, User, UserCreate, UserUpdate, ReadUsersQP


router = APIRouter()


@router.get(
    "/",
    response_model=UsersResponse,
    response_model_by_alias=False,
    response_description="Operation successful.",
    description="Returns the users matching the given query params from the database.",
    summary="Read Users"
)
@ensure_authority(mode="admin")
async def read_users(user: User, qp: ReadUsersQP):
    return UsersResponse(users=await Manager.get_all_or_fail(collection, qp))


@router.get(
    "/{object_id}/",
    response_model=UserResponse,
    response_model_by_alias=False,
    response_description="Operation successful.",
    description="Returns the user with the given object_id from the database.",
    summary="Read User"
)
@ensure_authority("normal")
async def read_user(user: User, object_id: ObjectID):
    return await Manager.get_or_fail(collection, {"_id": bson.ObjectId(object_id)})


@router.post(
    "/",
    response_model=UserResponse,
    response_model_by_alias=False,
    response_description="Operation successful.",
    description="Creates a user and returns the user object.",
    summary="Create User",
    status_code=status.HTTP_201_CREATED
)
async def create_user(body: UserCreate):
    new_user = await Manager.create_or_fail(collection, body.model_dump())
    created_user = await Manager.get_or_fail(collection, {"_id": bson.ObjectId(new_user.inserted_id)})
    return created_user


@router.put(
    "/{object_id}/",
    response_model=UserResponse,
    response_model_by_alias=False,
    response_description="Operation successful.",
    description="Updates the user with the given object_id and returns the user object.",
    summary="Update User"
)
@ensure_authority("normal")
async def update_user(user: User, object_id: ObjectID, body: UserUpdate):
    body = body.absolute_model_dump()
    if len(body) < 1:
        return await Manager.get_or_fail(collection, {"_id": bson.ObjectId(object_id)})
    else:
        return await Manager.update_or_fail(collection, object_id, "$set", body)


@router.delete(
    "/{object_id}/",
    response_description="Operation successful.",
    summary="Delete User",
    description="Deletes the user with the given object_id.",
    status_code=status.HTTP_204_NO_CONTENT
)
@ensure_authority("normal")
async def delete_user(user: User, object_id: ObjectID):
    await Manager.delete_or_fail(collection, object_id)
