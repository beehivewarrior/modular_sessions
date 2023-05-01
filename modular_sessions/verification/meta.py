"""
Class for verifying the session token
"""

from abc import abstractmethod
from typing import Generic

from fastapi import HTTPException, Request

from modular_sessions.backends.meta import SessionBackendInterface
from modular_sessions.errors import BackendException, FrontendException
from modular_sessions.typing import SessionKey, SessionModel


class SessionVerificationInterface(Generic[SessionKey, SessionModel]):
    """
    An abstract interface for negotiating the verification of a session
    using different backend and frontend implementations.
    """

    async def __call__(self, request: Request) -> SessionModel:
        """
        Verify the session.

        :param request: Request.
        """
        try:
            session_id: SessionKey = request.state.session_ids[
                self.identifier
            ]

        except Exception:
            raise HTTPException(
                status_code=500, detail="Session ID could not be verified."
            ) from BackendException(f"failed to get session ID for {self.identifier} from request state.")

        if isinstance(session_id, FrontendException):
            raise self.session_http_exception

        session_data = await self.backend.load(session_id)

        if not session_data or not self.verify_session(session_data):
            raise self.session_http_exception

        return session_data

    @property
    @abstractmethod
    def backend(self) -> SessionBackendInterface[SessionKey, SessionModel]:
        """
        Session backend.
        """
        raise NotImplementedError()

    @property
    def session_http_exception(self) -> HTTPException:
        """
        HTTP exception for invalid session.
        """
        return HTTPException(
            status_code=400, detail="Session is invalid."
        )

    @property
    @abstractmethod
    def identifier(self) -> str:
        """
        Session Verification Identifier.
        """
        raise NotImplementedError()

    @abstractmethod
    def verify_session(self, model: SessionModel) -> bool:
        """
        Verify the session.

        :param model: Session model.
        :return: Session model.
        """
        raise NotImplementedError()


__all__ = ["SessionVerificationInterface", ]
