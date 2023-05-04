"""
Generics for session backends.
"""

import secrets
from abc import ABCMeta, abstractmethod
from typing import Generic, Optional

from modular_sessions.typing import SessionKey, SessionModel


class SessionBackendAbstract(Generic[SessionKey, SessionModel], metaclass=ABCMeta):
    """
    Abstract Interface for session backends.
    """

    key_byte_size = 16

    def __generate_session_key(self) -> SessionKey:
        """
        Default method to generate a session key.

        :return: Session key.
        """
        return secrets.token_urlsafe(self.key_byte_size)

    @abstractmethod
    async def create(self, key: SessionKey, session: SessionModel) -> None:
        """
        Create a session on the backend.

        :param key: Session key.
        :param session: Session.
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, key: SessionKey) -> None:
        """
        Delete a session from the backend.

        :param key: Session key.
        """
        raise NotImplementedError()

    @abstractmethod
    async def exists(self, key: SessionKey) -> bool:
        """
        Check if a session already exists on the backend.

        :param key: Session key.
        :return: True if the session exists, False otherwise.
        """
        raise NotImplementedError()

    # noinspection PyUnusedLocal
    async def generate_session_key(self) -> SessionKey:
        """
        Generate a session key.

        :return: Session key.
        """

        new_key = self.__generate_session_key()

        # if the key already exists, generate a new one
        if await self.exists(new_key):
            new_key = self.__generate_session_key()

        return new_key

    @abstractmethod
    async def invalidate(self, key: SessionKey) -> None:
        """
        Invalidate a session on the backend.

        :param key: Session key.
        """
        raise NotImplementedError()

    @abstractmethod
    async def load(self, key: SessionKey) -> Optional[SessionModel]:
        """
        Load a session from the backend.

        :param key: Session key.
        :return: Session.
        """
        raise NotImplementedError()

    @abstractmethod
    async def renew(self, key: SessionKey, ttl: Optional[int] = None) -> None:
        """
        Renew a session on the backend.

        :param key: Session key.
        :param ttl: Time to live.
        """
        raise NotImplementedError()

    @abstractmethod
    async def update(self, key: SessionKey, session: SessionModel, ttl: Optional[int] = None) -> None:
        """
        Update session data on the backend.

        :param key: Session key.
        :param session: Session.
        :param ttl: Time to live.
        """
        raise NotImplementedError()


__all__ = ["SessionBackendAbstract", ]
