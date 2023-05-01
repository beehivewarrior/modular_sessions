"""
Session Frontend that uses cookies.
"""

from typing import Optional

from fastapi import HTTPException, Response
from fastapi.openapi.models import APIKey, APIKeyIn
from itsdangerous import BadSignature, SignatureExpired, Signer, URLSafeTimedSerializer
from starlette.requests import Request

from modular_sessions.backends.meta import SessionBackendInterface
from modular_sessions.errors import InvalidCookie, SessionNotSet
from modular_sessions.frontends.meta import SessionFrontendInterface
from modular_sessions.schemas import SessionCookieParameters


class CookieSession(SessionFrontendInterface[str]):

    def __init__(self, *, cookie_name: str, identifier: str, secret_key: Optional[str] = None,
                 cookie_params: SessionCookieParameters = SessionCookieParameters(), scheme_name: Optional[str] = None,
                 backend_class: SessionBackendInterface = None):
        """
        Session Frontend that uses cookies.

        :param cookie_name: Cookie name.
        :param identifier: State Storage identifier.
        :param secret_key: Key used to sign the cookie.
        :param cookie_params: Cookie parameters to always use.
        :param scheme_name: Scheme name.
        :param backend_class: Backend class.
        """

        self.backend_class = backend_class or self.backend_class
        self.model: APIKey = APIKey(**{"in": APIKeyIn.cookie}, name=cookie_name)
        self.scheme_name = scheme_name or self.__class__.__name__

        self.__identifier = identifier
        self.__secret_key = secret_key or self.backend_class.secret_key
        self.__serializer = URLSafeTimedSerializer(
            self.backend_class.secret_key, salt=self.backend_class.signer_salt, signer=Signer
        )
        self.__cookie_params = cookie_params.copy(deep=True)

    def __call__(self, request: Request) -> str:
        """
        Retrieve the session from the request.
        """

        signed_session_id = request.cookies.get(self.model.name)

        if not signed_session_id:
            raise SessionNotSet() from HTTPException(status_code=401, detail="Session not found.")

        try:
            session_id = self.__serializer.loads(signed_session_id, max_age=self.__cookie_params.max_age,
                                                 return_timestamp=False)
        except (BadSignature, SignatureExpired):
            raise HTTPException(status_code=401, detail="Invalid session.") from InvalidCookie()

        super().add_session_key_to_state(request, session_id)
        return session_id

    @property
    def identifier(self) -> str:
        """
        Frontend identifier.
        """

        return self.__identifier

    def open_session(self, resp: Response, session_key: str) -> None:
        """
        Attach a session to a response.

        :param resp:
        :param session_key:
        :return:
        """

        resp.set_cookie(
            key=self.model.name,
            value=str(self.__serializer.dumps(session_key)),
            **self.__cookie_params.dict(),
        )

    def remove_session(self, resp: Response) -> None:
        """
        Remove a session from a response.

        :param resp: The response.
        """

        resp.delete_cookie(
            key=self.model.name,
        )


__all__ = ["CookieSession", ]
