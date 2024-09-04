from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from bson import ObjectId

from core.exceptions import ChatAppAPIError, EntityDoesNotExistError, EntityAlreadyExistsError


async def get_or_fail(collection: str, body: dict, db: AsyncIOMotorDatabase, exc: ChatAppAPIError = None) -> dict:
    if (
        res := await db[collection].find_one(body)
    ) is not None:
        return res
    else:
        if exc is not None:
            raise exc
        else:
            raise EntityDoesNotExistError(
                detail=f"Document with {body} not found in the {collection=}."
            )


async def get_all_or_fail(collection: str, qp: Any, db: AsyncIOMotorDatabase) -> list:
    res = await db[collection] \
        .find() \
        .sort(qp.order_by, qp.order_direction) \
        .skip(qp.skip) \
        .limit(qp.limit) \
        .to_list(length=qp.limit)
    if len(res) > 0:
        return res
    else:
        raise EntityDoesNotExistError(
            detail=f"Documents with {qp=} not found in the {collection=}."
        )


async def create_or_fail(collection: str, body: dict, db: AsyncIOMotorDatabase) -> dict:
    try:
        return await db[collection].insert_one(body)
    except DuplicateKeyError:
        raise EntityAlreadyExistsError


async def update_or_fail(collection: str, object_id: str, body: dict, db: AsyncIOMotorDatabase) -> dict:
    try:
        if (
            res := await db[collection].find_one_and_update(
                {"_id": ObjectId(object_id)},
                {"$set": body},
                return_document=ReturnDocument.AFTER
            )
        ) is not None:
            return res
        else:
            raise EntityDoesNotExistError(
                detail=f"Document with {object_id=} not found in the {collection=}."
            )
    except DuplicateKeyError:
        raise EntityAlreadyExistsError


async def delete_or_fail(collection: str, object_id: str, db: AsyncIOMotorDatabase) -> None:
    res = await db[collection].find_one_and_delete({"_id": ObjectId(object_id)})
    if res is None:
        raise EntityDoesNotExistError(
            detail=f"Document with {object_id=} not found in the {collection=}."
        )
