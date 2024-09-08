from typing import Literal, List, Tuple
from getpass import getpass

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel

from .hash import hash_password as hp
from .logging import log
from . import settings


class ConnectionManager:
    _client: AsyncIOMotorClient = None

    def __enter__(self):
        ConnectionManager._client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE
        )
        log.info("Connected to the database.")
        return ConnectionManager._client

    def __exit__(self, exc_type, exc_value, traceback):
        if ConnectionManager._client is not None:
            ConnectionManager._client.close()
            ConnectionManager._client = None
        log.info("Disconnected from the database.")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        return cls._client[settings.MONGODB_DATABASE_NAME]

    @classmethod
    async def create_super_user(cls):
        with cls() as client:
            username = input("Enter username: ") or settings.ADMIN_DEFAULT_USERNAME
            email = input("Enter email: ") or settings.ADMIN_DEFAULT_EMAIL
            password = getpass("Enter password: ") or settings.ADMIN_DEFAULT_PASSWORD

            await client[settings.MONGODB_DATABASE_NAME][settings.USERS_COLLECTION].insert_one(
                {"username": username, "email": email, "password": hp(password), "is_admin": True}
            )
            log.info("Super user created successfully.")


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
        if ConnectionManager._client is None:
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
                await ConnectionManager._client[settings.MONGODB_DATABASE_NAME][res.collection].create_index([u], unique=True)
            log.info(f"Successfully created {res.unique} index on the {res.collection}.")
