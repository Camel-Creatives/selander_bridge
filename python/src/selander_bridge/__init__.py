"""
selander_bridge
===============

A reusable bridge between Python apps and Google Workspace APIs
(Drive, Contacts, and easy to extend to more).

Quick start (personal / per-developer Google accounts, no hosting needed):

    from selander_bridge import GoogleAuthManager, ContactsClient, DriveClient

    auth = GoogleAuthManager(
        client_secrets_file="client_secret.json",
        scopes=[*ContactsClient.scopes, *DriveClient.scopes],
    )

    contacts = ContactsClient(auth, account="me@gmail.com")
    for person in contacts.list_contacts():
        print(person.get("names"))

    drive = DriveClient(auth, account="me@gmail.com")
    for f in drive.list_files(query="mimeType='application/vnd.google-apps.folder'"):
        print(f["name"])

Quick start (Google Workspace org you administer, zero browser interaction):

    from selander_bridge import ServiceAccountAuthManager, DriveClient

    auth = ServiceAccountAuthManager(
        service_account_file="service_account.json",
        scopes=DriveClient.scopes,
    )
    drive = DriveClient(auth, account="someuser@yourcompany.com")
"""

from .auth import GoogleAuthManager, ServiceAccountAuthManager, TokenStore
from .base import BaseService
from .contacts import ContactsClient, SCOPE_CONTACTS, SCOPE_CONTACTS_READONLY
from .drive import DriveClient
from .exceptions import (
    AuthenticationError,
    MissingClientSecretsError,
    SelanderBridgeError,
)

__version__ = "0.1.1"

__all__ = [
    "GoogleAuthManager",
    "ServiceAccountAuthManager",
    "TokenStore",
    "BaseService",
    "ContactsClient",
    "SCOPE_CONTACTS",
    "SCOPE_CONTACTS_READONLY",
    "DriveClient",
    "SelanderBridgeError",
    "AuthenticationError",
    "MissingClientSecretsError",
]
