"""
Schemas used for sessions
"""

from typing import Optional

from pydantic import BaseModel


class SessionCookieParameters(BaseModel):
    """
    Session cookie.
    """

    domain: Optional[str] = None
    max_age: int = 3600


class UserSession(BaseModel):
    """
    User session.
    """

    session_id: str


__all__ = ["SessionCookieParameters", "UserSession"]
