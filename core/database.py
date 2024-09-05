from typing import List, Tuple
from enum import Enum

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, field_validator

from .logging import log
from . import settings


class ConnectionManager:
    client: AsyncIOMotorClient = None

    def __enter__(self):
        ConnectionManager.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE
        )
        log.info("Connected to the database.")
        return ConnectionManager.client

    def __exit__(self, exc_type, exc_value, traceback):
        if ConnectionManager.client is not None:
            ConnectionManager.client.close()
            ConnectionManager.client = None
        log.info("Disconnected from the database.")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        return cls.client[settings.MONGODB_DATABASE_NAME]


class Migration:
    """
    Inherit from this class to create unique indexes on the corresponding MongoDB collection.

    You must create the following class variables:
        collection: ClassVar[str] -> The name of the collection.
        unique: ClassVar[List[Tuple[str, int]]] -> The list of fields and indexing orders.

    Example Use Case:
        class User(Migration):
            collection: ClassVar = "users"
            unique: ClassVar = [("username", 1), ("email", -1)]
    """

    class CollectionUniqueModel(BaseModel):
        class IndexOrderEnum(Enum):
            ONE = 1
            MINUS_ONE = -1

        collection: str
        unique: List[Tuple[str, IndexOrderEnum]]

        @field_validator('unique', mode='after')
        def convert_unique(cls, value):
            return [(field, index_order.value) for field, index_order in value]

    @classmethod
    async def commit(cls):
        assert ConnectionManager.client is not None, "Database client does not exist."

        for subclass in cls.__subclasses__():
            assert hasattr(subclass, "collection"), f"{subclass.__name__} must have a 'collection' attribute."
            assert hasattr(subclass, "unique"), f"{subclass.__name__} must have a 'unique' attribute."

            res = cls.CollectionUniqueModel(
                collection=subclass.collection,
                unique=subclass.unique
            )

            for u in res.unique:
                await ConnectionManager.client[settings.MONGODB_DATABASE_NAME][res.collection].create_index([u], unique=True)
            log.info(f"Successfully created {res.unique} index on the {res.collection}.")
