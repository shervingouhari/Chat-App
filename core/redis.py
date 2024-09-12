from redis.asyncio import Redis

from .logging import log
from . import settings


class Manager:
    _db: Redis = None

    async def __aenter__(self):
        Manager._db = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        log.info("Connected to Redis.")
        return Manager._db

    async def __aexit__(self, exc_type, exc_value, traceback):
        if Manager._db is not None:
            await Manager._db.flushdb()
            await Manager._db.close()
            Manager._db = None
        log.info("Disconnected from Redis.")

    @classmethod
    def get_db(cls) -> Redis:
        return cls._db
