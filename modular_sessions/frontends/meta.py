"""
Generics for session frontends.
"""

from abc import ABCMeta, abstractmethod
from typing import Generic

from fastapi import Request, Response

from modular_sessions.backends.memory import MemoryBackend
from modular_sessions.typing import SessionKey, SessionAppendage


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
    def open_session(self, session_key: SessionKey) -> SessionAppendage:
        """
        Attach a session to a response.

        :param session_key: Session key.
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
