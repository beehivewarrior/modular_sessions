"""
Redis Backend for API Sessions.
"""

from typing import Optional, Type

from modular_sessions.errors import SessionNotFound, SessionAlreadyExists
from modular_sessions.typing import EngineType, SessionKey, SessionModel
from .meta import SessionBackendAbstract


class RedisHashSetBackend(SessionBackendAbstract[SessionKey, SessionModel]):
    """
    Redis Backend for API Sessions.

    Uses a Redis Hash Set to store session data.
    """

    def __init__(self, session_model: Type[SessionModel], redis: EngineType, default_ttl: int = 3600,
                 expire_on_delete: bool = True):
        """
        Initialize the Redis Backend.

        :param session_model: Session model.
        :param redis: Redis engine.
        :param default_ttl: Default TTL for sessions. Defaults to 3600 seconds (1 hour).
        :param expire_on_delete: Expire the session instead of deleting it. Defaults to True.
        """
        self.model = session_model
        self.redis = redis
        self.default_ttl = default_ttl
        self.expire_on_delete = expire_on_delete

    async def create(self, key: SessionKey, session: SessionModel, ttl: Optional[int] = None) -> None:
        """
        Create a session on the backend.

        :param key: Session key.
        :param session: Session.
        :param ttl: Session TTL in seconds. Defaults to 3600 seconds (1 hour).
        """

        if await self.exists(key):
            raise SessionAlreadyExists(f"Session {key} already exists on the backend. Cannot overwrite!")

        await self.redis.hset(key, mapping=session.dict())
        await self.redis.expire(key, ttl or self.default_ttl)

    async def delete(self, key: SessionKey) -> None:
        """
        Delete a session from the backend.

        :param key: Session key.
        """

        if not await self.exists(key):
            raise SessionNotFound(f"Session {key} not found on the backend. Cannot delete what doesn't exist!")

        elif self.expire_on_delete:
            await self.redis.expire(key, 0)

        else:
            await self.redis.delete(key)

    async def exists(self, key: SessionKey) -> bool:
        """
        Check if a session already exists on the backend.

        :param key: Session key.
        :return: True if the session exists, False otherwise.
        """

        exists = await self.redis.exists(key)
        return bool(exists)

    async def invalidate(self, key: SessionKey) -> None:
        """
        Invalidate a session on the backend.

        :param key: Session key.
        """

        if not await self.exists(key):
            raise SessionNotFound(f"Session {key} not found on the backend. Cannot invalidate what doesn't exist!")

        await self.redis.expire(key, 0)

    async def load(self, key: SessionKey) -> Optional[SessionModel]:
        """
        Load a session from the backend.

        :param key: Session key.
        :return: Session.
        """

        if not await self.exists(key):
            raise SessionNotFound(f"Session {key} not found on the backend. Cannot load what doesn't exist!")

        session = await self.redis.hgetall(key)
        return self.model(**session) if session else None

    async def renew(self, key: SessionKey, ttl: Optional[int] = None) -> None:
        """
        Renew a session on the backend.

        :param key: Session key.
        :param ttl: Session TTL in seconds. Overrides the default TTL.
        """

        if not await self.exists(key):
            raise SessionNotFound(f"Session {key} not found on the backend. Cannot renew what doesn't exist!")

        await self.redis.expire(key, ttl or self.default_ttl)

    async def update(self, key: SessionKey, session: SessionModel, ttl: Optional[int] = None) -> None:
        """
        Update a session on the backend.
        Will create the session if it doesn't exist.

        :param key: Session key.
        :param session: Session.
        :param ttl: Session TTL in seconds. Overrides the default TTL if the session didn't exist before.
        """

        # If the session doesn't exist, create it instead.
        if not await self.exists(key):
            return await self.create(key, session, ttl)

        await self.redis.hset(key, mapping=session.dict())

        if ttl:
            await self.redis.expire(key, ttl)


__all__ = ["RedisHashSetBackend", ]
