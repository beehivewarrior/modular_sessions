"""
An in-memory session store.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Type, Union

from modular_sessions.errors import SessionNotFound, SessionAlreadyExists
from modular_sessions.typing import SessionKey, SessionModel

from .meta import SessionBackendInterface


class MemoryBackend(SessionBackendInterface[SessionKey, SessionModel]):
    """
    In-Memory Backend for API Sessions.

    Stores sessions in a dictionary.
    """

    key_byte_size = 4

    def __init__(self, session_model: Type[SessionModel], default_ttl: int = 3600):
        """
        Initialize the In-Memory Backend.

        :param session_model: Session model.
        :param default_ttl: Default TTL for sessions. Defaults to 3600 seconds (1 hour).
        """
        self.model = session_model
        self.default_ttl = default_ttl
        self.sessions: Dict[SessionKey, Dict[str, Union[SessionModel, int]]] = {}

    async def create(self, key: SessionKey, session: SessionModel, ttl: Optional[int] = None) -> None:
        """
        Create a session on the backend.

        :param key: Session key.
        :param session: Session.
        :param ttl: Session TTL in seconds. Defaults to 3600 seconds (1 hour).
        """

        if await self.exists(key):
            raise SessionAlreadyExists(f"Session {key} already exists on the backend. Cannot overwrite!")

        # Calculate the expiration time
        expires = datetime.utcnow() + timedelta(seconds=ttl or self.default_ttl)

        # Store the session as a deep copy to prevent accidental modification
        self.sessions[key] = {"session": session.copy(deep=True), "expires": expires}

    async def delete(self, key: SessionKey) -> None:
        """
        Delete a session from the backend.

        :param key: Session key.
        """

        if not await self.exists(key):
            raise SessionNotFound(f"Session {key} not found on the backend. Cannot delete what doesn't exist!")

        del self.sessions[key]

    async def exists(self, key: SessionKey) -> bool:
        """
        Check if a session already exists on the backend.

        :param key: Session key.
        :return: True if the session exists, False otherwise.
        """

        return key in self.sessions

    async def invalidate(self, key: SessionKey) -> None:
        """
        Invalidate a session on the backend.

        :param key: Session key.
        """

        if not await self.exists(key):
            raise SessionNotFound(f"Session {key} not found on the backend. Cannot invalidate what doesn't exist!")

        self.sessions[key]["expires"] = datetime.utcnow()

    async def load(self, key: SessionKey) -> Optional[SessionModel]:
        """
        Load a session from the backend.

        :param key: Session key.
        :return: Session.
        """

        if not await self.exists(key):
            raise SessionNotFound(f"Session {key} not found on the backend. Cannot load what doesn't exist!")

        return self.model(**self.sessions[key]["session"].dict())

    async def renew(self, key: SessionKey, ttl: Optional[int] = None) -> None:
        """
        Renew a session on the backend.

        :param key: Session key.
        :param ttl: Session TTL in seconds. Overrides the default TTL.
        """

        if not await self.exists(key):
            raise SessionNotFound(f"Session {key} not found on the backend. Cannot renew what doesn't exist!")

        # Calculate the expiration time
        expires = datetime.utcnow() + timedelta(seconds=ttl or self.default_ttl)

        # Update the expiration time
        self.sessions[key]["expires"] = expires

    async def update(self, key: SessionKey, session: SessionModel, ttl: Optional[int] = None) -> None:
        """
        Update a session on the backend.

        :param key: Session key.
        :param session: Session.
        :param ttl: Session TTL in seconds. Overrides the default TTL if the session didn't exist before.
        """

        if not await self.exists(key):
            return await self.create(key, session, ttl)

        # Update the session and expiration time
        self.sessions[key]["session"] = session.copy(deep=True)

        if ttl:
            # Calculate the expiration time
            expires = datetime.utcnow() + timedelta(seconds=ttl or self.default_ttl)
            self.sessions[key]["expires"] = expires


__all__ = ["MemoryBackend", ]
