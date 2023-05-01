"""
Exceptions for sessions
"""


class SessionException(Exception):
    """
    Base Exception for sessions.
    """
    pass


class BackendException(SessionException):
    """
    Base Exception for session backends.
    """
    pass


class FrontendException(SessionException):
    """
    Base Exception for session frontends.
    """
    pass


class VerificationException(SessionException):
    """
    Base Exception for session verification.
    """
    pass


class SessionNotFound(BackendException):
    """
    Exception raised when a session is not found on the backend.
    """
    pass


class SessionAlreadyExists(BackendException):
    """
    Exception raised when a session already exists on the backend.
    """
    pass


class InvalidCookie(FrontendException):
    """
    Exception raised when a cookie is invalid.
    """
    pass


class SessionNotSet(FrontendException):
    """
    Exception raised when a session is not set.
    """
    pass


__all__ = [
    "SessionException", "BackendException", "FrontendException", "VerificationException", "SessionNotFound",
    "SessionAlreadyExists", "InvalidCookie", "SessionNotSet"
]
