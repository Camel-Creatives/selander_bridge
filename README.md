# selander_bridge

A small, reusable Python library that bridges your apps to Google accounts
and Google Workspace services (Drive, Contacts, more to come) — built once,
imported everywhere, with **no server you have to host** for auth.

## Why this exists

The standard "web app" OAuth flow needs a permanently running, publicly
reachable URL to catch Google's redirect. That's the "too much hosting"
problem. `selander_bridge` defaults to Google's **installed-app / loopback
flow** instead: a browser opens, you log in, Google redirects to a local
port that only exists for a few seconds, and the resulting refresh token is
cached to disk. Every app that imports this library and reuses the same
`account` key skips the login screen after the first time.

If every account you need belongs to a Workspace domain you administer,
you can skip browser login entirely with `ServiceAccountAuthManager`
(domain-wide delegation) — zero hosting, zero interaction.

## Install

```bash
pip install -e .
```

(Once you're happy with it, `pip install build twine` and publish it to
your own PyPI-compatible index or a private Git URL so other projects can
`pip install` it directly.)

## One-time Google Cloud setup

1. Create/select a project at console.cloud.google.com.
2. Enable the **Drive API** and **People API**.
3. Create OAuth client credentials of type **Desktop app** (not "Web
   application" — that's what forces hosting). Download the JSON as
   `client_secret.json`.
4. (Personal Gmail accounts) On the OAuth consent screen, add yourself as
   a test user, or publish the app if you'll use this with other people's
   accounts.

## Usage

```python
from selander_bridge import GoogleAuthManager, ContactsClient, DriveClient

auth = GoogleAuthManager(
    client_secrets_file="client_secret.json",
    scopes=[*ContactsClient.scopes, *DriveClient.scopes],
)

# First call opens a browser once; after that, the cached token is reused.
contacts = ContactsClient(auth, account="me@gmail.com")
for person in contacts.list_contacts():
    print(person.get("names"))

drive = DriveClient(auth, account="me@gmail.com")
drive.upload_file("report.pdf", name="Q2 Report.pdf")
```

Use a different `account` string per Google account you need to talk to —
each gets its own cached token under `~/.selander_bridge/tokens/`.

## Extending to more Workspace APIs

Every wrapper follows the same shape. To add Calendar, Sheets, Gmail, etc.,
copy `drive.py` as a template:

```python
from .base import BaseService, wrap_http_errors

class CalendarClient(BaseService):
    api_name = "calendar"
    api_version = "v3"
    scopes = ("https://www.googleapis.com/auth/calendar.readonly",)

    @wrap_http_errors
    def list_events(self, calendar_id="primary", max_results=50):
        resp = self.service.events().list(
            calendarId=calendar_id, maxResults=max_results
        ).execute()
        return resp.get("items", [])
```

Then export it from `selander_bridge/__init__.py`.

## Project layout

```
selander_bridge/
├── pyproject.toml
├── README.md
├── src/selander_bridge/
│   ├── __init__.py     # public exports
│   ├── auth.py         # GoogleAuthManager, ServiceAccountAuthManager, TokenStore
│   ├── base.py         # BaseService (shared plumbing), wrap_http_errors
│   ├── contacts.py     # ContactsClient (People API)
│   ├── drive.py        # DriveClient
│   └── exceptions.py
└── tests/
    └── test_imports.py
```
