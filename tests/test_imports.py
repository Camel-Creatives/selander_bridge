"""
Smoke tests for selander_bridge. These never touch the network - they verify
imports, class shapes, and the auth/token-store plumbing using fakes.
"""
from unittest.mock import MagicMock, patch

import pytest

from selander_bridge import (
    AuthenticationError,
    ContactsClient,
    DriveClient,
    GoogleAuthManager,
    SelanderBridgeError,
    ServiceAccountAuthManager,
    TokenStore,
)
from selander_bridge.exceptions import MissingClientSecretsError


def test_public_exports_importable():
    assert GoogleAuthManager and ServiceAccountAuthManager and TokenStore
    assert ContactsClient and DriveClient
    assert AuthenticationError and SelanderBridgeError


def test_contacts_client_has_expected_scope():
    assert "contacts" in ContactsClient.scopes[0]


def test_drive_client_has_expected_scope():
    assert "drive" in DriveClient.scopes[0]


def test_missing_client_secrets_raises(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(MissingClientSecretsError):
        GoogleAuthManager(client_secrets_file=missing, scopes=["scope_a"])


def test_token_store_round_trip(tmp_path):
    store = TokenStore(base_dir=tmp_path)
    fake_creds = MagicMock()
    fake_creds.to_json.return_value = (
        '{"token": "abc", "refresh_token": "r1", "scopes": ["scope_a"], '
        '"client_id": "cid", "client_secret": "csecret"}'
    )

    store.save("someone@example.com", fake_creds)
    path = store._path("someone@example.com")
    assert path.exists()

    loaded = store.load("someone@example.com")
    assert loaded.token == "abc"
    assert loaded.refresh_token == "r1"

    store.delete("someone@example.com")
    assert not path.exists()


def test_get_credentials_uses_cached_valid_token(tmp_path):
    secrets_file = tmp_path / "client_secret.json"
    secrets_file.write_text("{}")

    store = TokenStore(base_dir=tmp_path / "tokens")
    auth = GoogleAuthManager(client_secrets_file=secrets_file, scopes=["scope_a"], token_store=store)

    fake_creds = MagicMock()
    fake_creds.valid = True
    fake_creds.scopes = ["scope_a"]
    store.load = MagicMock(return_value=fake_creds)

    with patch.object(auth, "_run_interactive_flow") as run_flow:
        result = auth.get_credentials("someone@example.com")
        run_flow.assert_not_called()
        assert result is fake_creds


def test_get_credentials_falls_back_to_interactive_flow_when_no_cache(tmp_path):
    secrets_file = tmp_path / "client_secret.json"
    secrets_file.write_text("{}")

    store = TokenStore(base_dir=tmp_path / "tokens")
    auth = GoogleAuthManager(client_secrets_file=secrets_file, scopes=["scope_a"], token_store=store)
    store.load = MagicMock(return_value=None)
    store.save = MagicMock()

    fake_new_creds = MagicMock()
    with patch.object(auth, "_run_interactive_flow", return_value=fake_new_creds) as run_flow:
        result = auth.get_credentials("someone@example.com")
        run_flow.assert_called_once()
        store.save.assert_called_once_with("someone@example.com", fake_new_creds)
        assert result is fake_new_creds


def test_base_service_builds_resource_lazily():
    fake_auth = MagicMock()
    fake_auth.get_credentials.return_value = "fake-creds"

    with patch("selander_bridge.base.build") as mock_build:
        mock_build.return_value = "fake-resource"
        client = DriveClient(fake_auth, account="me@example.com")

        # Not called yet - lazy.
        fake_auth.get_credentials.assert_not_called()

        resource = client.service
        fake_auth.get_credentials.assert_called_once_with("me@example.com")
        mock_build.assert_called_once_with("drive", "v3", credentials="fake-creds")
        assert resource == "fake-resource"

        # Second access should not rebuild.
        _ = client.service
        mock_build.assert_called_once()
