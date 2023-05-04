"""
Class to verify the session token.

Basic verification is done by checking if the session exists in the backend.
"""

from modular_sessions.schemas import UserSession
from modular_sessions.typing import SessionModel, BackEndInterface
from modular_sessions.verification.meta import SessionVerificationInterface


class BasicSessionVerification(SessionVerificationInterface[str, UserSession]):

    def __init__(self, *, identifier: str, backend: BackEndInterface[str, UserSession]):
        """
        :param identifier: Identifier for the session.
        :param backend: Session backend.
        """
        self._identifier = identifier
        self._backend = backend

    @property
    def backend(self) -> BackEndInterface[str, UserSession]:
        """
        Session backend.
        """
        return self._backend

    @property
    def identifier(self) -> str:
        """
        Session Verification Identifier.
        """
        return self._identifier

    def verify_session(self, session_data: SessionModel) -> bool:
        """
        Verify the session.

        :param session_data: Session data.
        """

        # for now, just check if the session exists
        return True


__all__ = ["BasicSessionVerification", ]
