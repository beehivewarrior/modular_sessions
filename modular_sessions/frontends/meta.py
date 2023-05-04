"""
Generics for session frontends.
"""

from abc import ABCMeta, abstractmethod
from typing import Generic, Type

from fastapi import Request, Response
from itsdangerous import Signer, Serializer
from starlette.datastructures import MutableHeaders

from modular_sessions.backends.memory import MemoryBackend
from modular_sessions.typing import SessionKey


class SessionFrontendAbstract(Generic[SessionKey], metaclass=ABCMeta):
    """
    Abstract Interface for session frontends.
    """

    backend_class = MemoryBackend

    @property
    @abstractmethod
    def identifier(self) -> str:
        """
        Frontend identifier.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def serializer(self) -> Serializer:
        """
        Serializer used to sign session data
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def signer(self) -> Type[Signer]:
        """
        Data signing class
        """
        raise NotImplementedError()

    def add_session_key_to_state(self, req: Request, session_id: SessionKey) -> None:
        """
        Add session key to request state.

        :param req: Request.
        :param session_id: Session ID.
        """

        # noinspection PyBroadException
        try:
            req.state.session_ids[self.identifier] = session_id

        except Exception:
            req.state.session_ids = {self.identifier: session_id}

    @abstractmethod
    def open_session(self, session_key: SessionKey, headers: MutableHeaders) -> MutableHeaders:
        """
        Attach a session to a response.

        :param session_key: Session key.
        :param headers: Headers to manipulate
        """
        raise NotImplementedError()

    @abstractmethod
    def remove_session(self, resp: Response) -> None:
        """
        Remove a session from a response.

        :param resp: Response.
        """
        raise NotImplementedError()


__all__ = ["SessionFrontendAbstract", ]
