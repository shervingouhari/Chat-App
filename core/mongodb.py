from typing import Any, Literal, List, Tuple
from getpass import getpass

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from bson import ObjectId
from pydantic import BaseModel

from core.exceptions import ChatAppAPIError, EntityDoesNotExistError, EntityAlreadyExistsError
from core.settings import MONGODB_URL, MONGODB_MAX_POOL_SIZE, MONGODB_MIN_POOL_SIZE, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_USERS
from .hash import hash_password as hp
from .logging import log


class Manager:
    _client: AsyncIOMotorClient = None

    def __enter__(self):
        Manager._client = AsyncIOMotorClient(
            MONGODB_URL,
            maxPoolSize=MONGODB_MAX_POOL_SIZE,
            minPoolSize=MONGODB_MIN_POOL_SIZE
        )
        log.info("Connected to MongoDB.")
        return Manager._client

    def __exit__(self, exc_type, exc_value, traceback):
        if Manager._client is not None:
            Manager._client.close()
            Manager._client = None
        log.info("Disconnected from MongoDB.")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        return cls._client[MONGODB_DATABASE_NAME]

    @classmethod
    async def create_super_user(cls):
        with cls() as client:
            username = input("Enter username: ")
            email = input("Enter email: ")
            password = getpass("Enter password: ")

            await client[MONGODB_DATABASE_NAME][MONGODB_COLLECTION_USERS].insert_one(
                {
                    "username": username,
                    "email": email,
                    "password": hp(password),
                    "is_admin": True
                }
            )
            log.info("Super user created successfully.")

    @classmethod
    async def get_or_fail(cls, collection: str, body: dict, exc: ChatAppAPIError = None) -> dict:
        if (res := await cls.get_db()[collection].find_one(body)) is not None:
            return res
        else:
            if exc is not None:
                raise exc
            else:
                raise EntityDoesNotExistError(
                    detail=f"Document with {body} not found in the {collection=}."
                )

    @classmethod
    async def get_all_or_fail(cls, collection: str, qp: Any) -> list:
        res = await cls.get_db()[collection] \
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

    @classmethod
    async def create_or_fail(cls, collection: str, body: dict) -> dict:
        try:
            return await cls.get_db()[collection].insert_one(body)
        except DuplicateKeyError:
            raise EntityAlreadyExistsError

    @classmethod
    async def update_or_fail(cls, collection: str, object_id: str, update_operator: str, body: dict) -> dict:
        try:
            if (
                res := await cls.get_db()[collection].find_one_and_update(
                    {"_id": ObjectId(object_id)},
                    {update_operator: body},
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

    @classmethod
    async def delete_or_fail(cls, collection: str, object_id: str) -> None:
        res = await cls.get_db()[collection].find_one_and_delete({"_id": ObjectId(object_id)})
        if res is None:
            raise EntityDoesNotExistError(
                detail=f"Document with {object_id=} not found in the {collection=}."
            )

    @classmethod
    async def get_or_create(cls, collection: str, body: dict) -> dict:
        try:
            return await cls.get_or_fail(collection, body)
        except EntityDoesNotExistError:
            return await cls.create_or_fail(collection, body)


class Migration:
    """
    Inherit from this class to create unique indexes on the corresponding MongoDB collection.

    You must create the following class variables:
        collection: ClassVar[str] -> The name of the collection.
        unique: ClassVarList[Tuple[str, Literal[1, -1]]] -> The list of fields and indexing orders.

    Example Use Case:
        class User(Migration):
            collection: ClassVar = "users"
            unique: ClassVar = [("username", 1), ("email", -1)]
    """

    class IndexSchema(BaseModel):
        collection: str
        unique: List[Tuple[str, Literal[1, -1]]]

    @classmethod
    async def commit(cls):
        with Manager() as _:
            for subclass in cls.__subclasses__():
                if not hasattr(subclass, "collection"):
                    raise ValueError(f"{subclass.__name__} must have a 'collection' attribute.")
                if not hasattr(subclass, "unique"):
                    raise ValueError(f"{subclass.__name__} must have a 'unique' attribute.")

                res = cls.IndexSchema(
                    collection=subclass.collection,
                    unique=subclass.unique
                )

                for u in res.unique:
                    await Manager.get_db()[res.collection].create_index([u], unique=True)
                log.info(f"Successfully created {res.unique} index on the {res.collection}.")
