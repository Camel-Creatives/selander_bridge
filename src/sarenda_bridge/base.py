"""Shared plumbing for every wrapped Google API."""
from __future__ import annotations

from typing import Any, Sequence

from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from .exceptions import SarendaBridgeError


class BaseService:
    """
    Base class every service wrapper (ContactsClient, DriveClient, ...)
    inherits from. Handles lazily building + caching the underlying
    googleapiclient Resource object the first time it's actually used.

    Works with either GoogleAuthManager (pass an account_key/email for
    `account`) or ServiceAccountAuthManager (pass the subject email to
    impersonate for `account`) -- both expose a one-argument
    `get_credentials(account)` method.
    """

    api_name: str
    api_version: str
    scopes: Sequence[str] = ()

    def __init__(self, auth_manager: Any, account: str = "default"):
        self._auth_manager = auth_manager
        self._account = account
        self._service: Resource | None = None

    @property
    def service(self) -> Resource:
        if self._service is None:
            creds = self._auth_manager.get_credentials(self._account)
            self._service = build(self.api_name, self.api_version, credentials=creds)
        return self._service


def wrap_http_errors(func):
    """Decorator that turns raw googleapiclient HttpError into a SarendaBridgeError."""

    def _wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as exc:
            raise SarendaBridgeError(f"Google API call failed: {exc}") from exc

    _wrapped.__name__ = func.__name__
    _wrapped.__doc__ = func.__doc__
    return _wrapped
