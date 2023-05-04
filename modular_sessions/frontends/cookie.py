"""
Session Frontend that uses cookies.
"""

from http.cookies import BaseCookie, SimpleCookie
from typing import Optional, Type

from fastapi import HTTPException, Response
from fastapi.openapi.models import APIKey, APIKeyIn
from itsdangerous import BadSignature, SignatureExpired, Signer, Serializer, URLSafeTimedSerializer
from starlette.datastructures import MutableHeaders
from starlette.requests import Request

from modular_sessions.errors import InvalidCookie, SessionNotSet
from modular_sessions.frontends.meta import SessionFrontendAbstract
from modular_sessions.schemas import SessionCookieParameters


class CookieSession(SessionFrontendAbstract[str]):

    def __init__(self, *, cookie_name: str, identifier: str, salt: str, secret_key: str,
                 cookie_params: SessionCookieParameters = SessionCookieParameters(), scheme_name: Optional[str] = None):
        """
        Session Frontend that uses cookies.

        :param cookie_name: Cookie name.
        :param identifier: State Storage identifier.
        :param secret_key: Key used to sign the cookie.
        :param cookie_params: Cookie parameters to always use.
        :param scheme_name: Scheme name.
        """

        self.model: APIKey = APIKey(**{"in": APIKeyIn.cookie}, name=cookie_name)
        self.scheme_name = scheme_name or self.__class__.__name__

        self.__identifier = identifier
        self.__salt = salt
        self.__secret_key = secret_key
        self.__serializer = None
        self.__cookie_params = cookie_params.copy(deep=True)

    def __call__(self, request: Request) -> str:
        """
        Retrieve the session from the request.
        """

        signed_session_id = request.cookies.get(self.model.name)

        if not signed_session_id:
            raise SessionNotSet() from HTTPException(status_code=401, detail="Session not found.")

        try:
            session_id = self.serializer.loads(signed_session_id, max_age=self.__cookie_params.max_age,
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

    @property
    def serializer(self) -> Serializer:
        if self.__serializer is None:
            self.__serializer = URLSafeTimedSerializer(self.__secret_key, salt=self.__salt, signer=self.signer)

        return self.__serializer

    @property
    def signer(self) -> Type[Signer]:
        return Signer

    def open_session(self, session_key: str, headers: MutableHeaders) -> MutableHeaders:
        """
        Attach a session to a response.

        :param session_key:
        :param headers:
        :return:
        """

        cookie: BaseCookie = SimpleCookie()
        cookie[self.model.name] = str(self.serializer.dumps(session_key))

        for k, v in self.__cookie_params.dict().items():
            cookie[self.model.name][k] = str(v)

        cookie_val = cookie.output(header="").strip()
        headers.append("Set-Cookie", cookie_val)

        return headers

    def remove_session(self, resp: Response) -> None:
        """
        Remove a session from a response.

        :param resp: The response.
        """

        resp.delete_cookie(
            key=self.model.name,
        )


__all__ = ["CookieSession", ]
