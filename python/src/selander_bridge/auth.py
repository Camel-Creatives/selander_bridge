"""
Authentication for selander_bridge.

The design goal here is specifically to avoid the "I need a hosted server
just to catch an OAuth redirect" problem. Instead of the web-application
OAuth flow (which needs a permanently running, publicly reachable callback
URL), this uses Google's installed-app / loopback flow:

    1. A browser window opens and the user logs into Google + consents.
    2. Google redirects to http://127.0.0.1:<random free port>/...
    3. A local HTTP server -- spun up only for this exchange, on a random
       free port, and torn down immediately after -- receives the
       authorization code and finishes the token exchange.
    4. The resulting refresh token is cached to disk (via TokenStore) so
       every later run, in any app that imports selander_bridge and uses the
       same `account_key`, picks the cached token up and never prompts again.

No server needs to be deployed or kept running anywhere for this to work.

If you're building a true multi-tenant web product where strangers need to
grant consent through your own domain, you'll still need *some* hosted
redirect endpoint for that flow specifically -- that's a Google requirement,
not a limitation of this library. Everything below still helps in that
case (token storage/refresh, the service wrappers), you'd just plug in a
different Flow object. See `GoogleAuthManager.from_web_flow` for a starting
point.

For the common Google Workspace admin case -- you control the whole
Workspace org and want to act on behalf of users in it -- a service account
with domain-wide delegation needs *zero* browser interaction and zero
hosting. See `ServiceAccountAuthManager` below.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Sequence, Union

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow

from .exceptions import AuthenticationError, MissingClientSecretsError

logger = logging.getLogger("selander_bridge.auth")

DEFAULT_TOKEN_DIR = Path.home() / ".selander_bridge" / "tokens"


class TokenStore:
    """
    Pluggable storage for cached OAuth credentials.

    Default implementation is one JSON file per `account_key` under
    ~/.selander_bridge/tokens/. Swap this out (same 3 methods) for a
    database- or keyring-backed store in a multi-user server app.
    """

    def __init__(self, base_dir: Optional[Union[str, Path]] = None):
        self.base_dir = Path(base_dir) if base_dir else DEFAULT_TOKEN_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, account_key: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "-_.@" else "_" for c in account_key)
        return self.base_dir / f"{safe}.json"

    def load(self, account_key: str) -> Optional[Credentials]:
        path = self._path(account_key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return Credentials.from_authorized_user_info(data)
        except (ValueError, KeyError) as exc:
            logger.warning("Could not parse cached token for %s: %s", account_key, exc)
            return None

    def save(self, account_key: str, creds: Credentials) -> None:
        self._path(account_key).write_text(creds.to_json())

    def delete(self, account_key: str) -> None:
        path = self._path(account_key)
        if path.exists():
            path.unlink()


class GoogleAuthManager:
    """
    Acquires and caches Google OAuth2 user credentials.

    Usage:
        auth = GoogleAuthManager(
            client_secrets_file="client_secret.json",
            scopes=ContactsClient.scopes + DriveClient.scopes,
        )
        creds = auth.get_credentials("someone@gmail.com")

    One `GoogleAuthManager` (and its scope list) is normally shared across
    every service wrapper in your app, so you only get one consent screen
    covering everything you need, per account.
    """

    def __init__(
        self,
        client_secrets_file: Union[str, Path],
        scopes: Sequence[str],
        token_store: Optional[TokenStore] = None,
    ):
        if not Path(client_secrets_file).exists():
            raise MissingClientSecretsError(
                f"client_secrets_file not found: {client_secrets_file}. "
                "Download this from Google Cloud Console > APIs & Services > "
                "Credentials > OAuth client ID (type: Desktop app)."
            )
        self.client_secrets_file = str(client_secrets_file)
        self.scopes = list(scopes)
        self.token_store = token_store or TokenStore()

    def get_credentials(self, account_key: str = "default") -> Credentials:
        """
        Return valid credentials for `account_key`, refreshing or running
        the interactive consent flow only if necessary.
        """
        creds = self.token_store.load(account_key)

        if creds and set(self.scopes) - set(creds.scopes or []):
            # Previously cached token doesn't cover everything requested now.
            logger.info("Cached scopes for %s are insufficient; re-authenticating", account_key)
            creds = None

        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self.token_store.save(account_key, creds)
                return creds
            except RefreshError as exc:
                logger.warning("Refresh failed for %s (%s); re-authenticating", account_key, exc)
                creds = None

        creds = self._run_interactive_flow()
        self.token_store.save(account_key, creds)
        return creds

    def _run_interactive_flow(self) -> Credentials:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, scopes=self.scopes
            )
            # port=0 -> OS picks a free local port; server shuts down right
            # after the redirect is caught. Nothing stays running.
            return flow.run_local_server(port=0)
        except Exception as exc:  # pragma: no cover - surfaced to caller
            raise AuthenticationError(f"Interactive Google sign-in failed: {exc}") from exc

    def forget(self, account_key: str) -> None:
        """Drop the cached token for an account, forcing re-auth next time."""
        self.token_store.delete(account_key)


class ServiceAccountAuthManager:
    """
    Zero-interaction, zero-hosting auth for Google Workspace admins.

    Use this instead of GoogleAuthManager when every account you need to
    touch belongs to a Workspace domain you administer. A super admin
    enables domain-wide delegation for a service account once, and from
    then on this manager can impersonate any user in the org with no
    browser, no consent screen, and no token caching needed (a fresh
    short-lived token is minted on every call).

    Setup (one-time, in Google Cloud Console + Workspace Admin console):
      1. Create a service account, generate a JSON key.
      2. Enable domain-wide delegation on it, note its OAuth Client ID.
      3. In admin.google.com > Security > API controls > Domain-wide
         delegation, authorize that client ID for the scopes you need.
    """

    def __init__(self, service_account_file: Union[str, Path], scopes: Sequence[str]):
        if not Path(service_account_file).exists():
            raise MissingClientSecretsError(
                f"service_account_file not found: {service_account_file}"
            )
        self.service_account_file = str(service_account_file)
        self.scopes = list(scopes)

    def get_credentials(self, subject: str) -> Credentials:
        """`subject` is the email of the Workspace user to impersonate."""
        try:
            return service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=self.scopes, subject=subject
            )
        except Exception as exc:
            raise AuthenticationError(f"Service-account auth failed for {subject}: {exc}") from exc
