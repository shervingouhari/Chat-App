from typing import Literal, List, Tuple
from getpass import getpass

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel
from redis.asyncio import Redis

from .hash import hash_password as hp
from .logging import log
from . import settings


class MongoDBConnectionManager:
    _client: AsyncIOMotorClient = None

    def __enter__(self):
        MongoDBConnectionManager._client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE
        )
        log.info("Connected to MongoDB.")
        return MongoDBConnectionManager._client

    def __exit__(self, exc_type, exc_value, traceback):
        if MongoDBConnectionManager._client is not None:
            MongoDBConnectionManager._client.close()
            MongoDBConnectionManager._client = None
        log.info("Disconnected from MongoDB.")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        return cls._client[settings.MONGODB_DATABASE_NAME]

    @classmethod
    async def create_super_user(cls):
        with cls() as client:
            username = input("Enter username: ")
            email = input("Enter email: ")
            password = getpass("Enter password: ")

            await client[settings.MONGODB_DATABASE_NAME][settings.USERS_COLLECTION].insert_one(
                {
                    "username": username,
                    "email": email,
                    "password": hp(password),
                    "is_admin": True
                }
            )
            log.info("Super user created successfully.")


class RedisConnectionManager:
    _db: Redis = None

    async def __aenter__(self):
        RedisConnectionManager._db = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        log.info("Connected to Redis.")
        return RedisConnectionManager._db

    async def __aexit__(self, exc_type, exc_value, traceback):
        if RedisConnectionManager._db is not None:
            await RedisConnectionManager._db.flushdb()
            await RedisConnectionManager._db.close()
            RedisConnectionManager._db = None
        log.info("Disconnected from Redis.")

    @classmethod
    def get_db(cls) -> Redis:
        return cls._db


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
        if MongoDBConnectionManager._client is None:
            raise RuntimeError("Database client is not initialized.")

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
                await MongoDBConnectionManager \
                    ._client[settings.MONGODB_DATABASE_NAME][res.collection] \
                    .create_index([u], unique=True)
            log.info(f"Successfully created {res.unique} index on the {res.collection}.")
