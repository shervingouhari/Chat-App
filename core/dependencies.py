from motor.motor_asyncio import AsyncIOMotorDatabase

from core import settings


async def get_db() -> AsyncIOMotorDatabase:
    from core.database import client
    return client[settings.MONGODB_DATABASE_NAME]
