"""
Schemas used for sessions
"""

from typing import Optional

from pydantic import BaseModel, Field


class SessionCookieParameters(BaseModel):
    """
    Session cookie.
    """

    path = "/"
    max_age: int = Field(3600, alias="max-age", title="max-age")
    same_site: str = Field("lax", alias="same-site")


class UserSession(BaseModel):
    """
    User session.
    """

    session_id: str


__all__ = ["SessionCookieParameters", "UserSession"]
