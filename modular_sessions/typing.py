"""
Type Hints for the Session Middleware.
"""

from typing import Generic, Collection, Optional, Protocol, TypeVar, runtime_checkable

from aioredis.client import Redis
from fastapi import Response
from itsdangerous import Signer
from starlette.requests import Request as StarletteRequest
from pydantic import BaseModel


EngineType = TypeVar("EngineType", bound=Redis)

SessionKey = TypeVar("SessionKey")

SessionModel = TypeVar("SessionModel", bound=BaseModel)


@runtime_checkable
class SessionAppendage(Protocol):
    def output(self, attrs: Optional[Collection], header: Optional[str], sep: Optional[str]) -> (str, str): ...


class BackEndInterface(Generic[SessionKey, SessionModel]):
    async def create(self, key: SessionKey, session: SessionModel) -> None: ...
    async def delete(self, key: SessionKey) -> None: ...
    async def exists(self, key: SessionKey) -> bool: ...
    async def generate_session_key(self) -> SessionKey: ...
    async def invalidate(self, key: SessionKey) -> None: ...
    async def load(self, key: SessionKey) -> Optional[SessionModel]: ...
    async def renew(self, key: SessionKey, ttl: Optional[int] = None) -> None: ...
    async def update(self, key: SessionKey, session: SessionModel, ttl: Optional[int] = None) -> None: ...


class FrontEndInterface(Generic[SessionKey]):
    backend_class: BackEndInterface[SessionKey, SessionModel]
    identifier: str
    signer: Signer
    def __call__(self, *args, **kwargs): ...
    def open_session(self, session_key: SessionKey) -> SessionAppendage: ...
    def remove_session(self, resp: Response) -> None: ...


class VerificationInterface(Generic[SessionKey, SessionModel]):
    backend: BackEndInterface[SessionKey, SessionModel]
    identifier: str
    session_http_exception: Exception
    async def __call__(self, request: StarletteRequest) -> SessionModel: ...
    def verify_session(self, model: SessionModel) -> bool: ...


BackEndT = TypeVar("BackEndT", bound=BackEndInterface)
FrontEndT = TypeVar("FrontEndT", bound=FrontEndInterface)
VerificationT = TypeVar("VerificationT", bound=VerificationInterface)


__all__ = ["EngineType", "SessionKey", "SessionModel", "SessionAppendage", "BackEndT", "FrontEndT", "VerificationT"]
