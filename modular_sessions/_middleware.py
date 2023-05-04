"""
Middleware for sessions management on the API.
"""

import json
from typing import Optional, Type

from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection, HTTPException
from starlette.types import ASGIApp, Receive, Scope, Send, Message

from modular_sessions.errors import (
    SessionNotFound, SessionNotSet, VerificationException, BackendException
)
from modular_sessions.typing import FrontEndT, BackEndT, VerificationT, SessionModel


class SessionsMiddleware:
    """
    Middleware for sessions management on the API.
    """

    def __init__(self, app: ASGIApp, backend: BackEndT, frontend: FrontEndT,  model: Type[SessionModel],
                 verifier: VerificationT, renew_on_access: bool = True, renewal_ttl: Optional[int] = None) -> None:
        """
        Creates Middleware for sessions management on the API.

        :param app: FastAPI app.
        """

        self.app = app
        self.backend = backend
        self.frontend = frontend
        self.model = model
        self.renew_on_access = renew_on_access
        self.renewal_ttl = renewal_ttl
        self.verifier = verifier

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Middleware for sessions management on the API.

        :param scope: Scope.
        :param receive: Receive.
        :param send: Send.
        """

        replace_frontend_session = False
        update_backend_session = False

        session_id = await self.find_session_id(scope)

        try:
            session: Optional[SessionModel] = await self.backend.load(session_id)

        except SessionNotFound as _:
            # session ID was set, but it was not found in the backend
            # we will need to remove the session ID from the frontend
            replace_frontend_session = True
            session = None

        # now that we have the session ID, we need to verify it
        # if the session ID is invalid, we will need to remove it from the frontend
        is_valid = self.validate_session(session)

        # if the session ID is invalid, we will need to remove it from the frontend
        if not is_valid:
            replace_frontend_session = True
            update_backend_session = True
            session = None

        # run renewal if needed/requested
        if self.renew_on_access:
            try:
                # try to renew the session ID with the backend
                await self.backend.renew(session_id, self.renewal_ttl)

            except BackendException as b:
                # this error would be unexpected, and fatal
                raise HTTPException(
                    status_code=500, detail="Session ID could not be renewed."
                ) from b
        scope["session"] = json.loads(session.json())

        # borrowed from Starlette.SessionMiddleware for now
        async def response_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                if scope["session"]:
                    s_id = str(scope["session"]["session_id"])
                    headers = MutableHeaders(scope=message)
                    self.frontend.open_session(s_id, headers)

            await send(message)

        await self.app(scope, receive, response_wrapper)

    async def find_session_id(self, scope: Scope) -> Optional[str]:
        """
        Find the session ID in the scope.

        :param scope: Scope.
        :return: Session ID.
        """
        connection = HTTPConnection(scope)

        try:
            # try to load the session ID with the frontend
            session_id = await self.frontend(connection)

        except SessionNotSet as _:
            # if the session ID is not set, we will need to generate a new one
            session_id = await self.backend.generate_session_key()
            # we will need to set the session ID on the backend
            new_session: SessionModel = self.model(session_id=session_id)
            await self.backend.create(session_id, new_session)

        return session_id

    def validate_session(self, session: SessionModel) -> bool:
        """
        Validate the session.

        :param session: Session.
        :return: True if valid, False otherwise.
        """

        is_valid = False

        try:

            if issubclass(session.__class__, self.model):
                is_valid = self.verifier.verify_session(session)

        except VerificationException as _:
            is_valid = False

        return is_valid


__all__ = ["SessionsMiddleware", ]
