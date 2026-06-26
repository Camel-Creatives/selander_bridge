# Authentication

`selander_bridge` provides two main ways to authenticate, designed to avoid the hassle of running a permanent web server for OAuth redirects.

## 1. GoogleAuthManager (Interactive User Auth)

`GoogleAuthManager` is used when you need individual users to authorize your application to access their Google data. It uses the installed-app (loopback) flow.

### How it works:
1. A browser window opens, prompting the user to log in and consent.
2. Google redirects to a temporary local HTTP server (`http://127.0.0.1:<random_port>`).
3. The server catches the authorization code and immediately shuts down.
4. The token is cached to disk in `~/.selander_bridge/tokens/`. Subsequent runs will reuse this token without prompting the user.

### Usage Example:
```python
from selander_bridge import GoogleAuthManager, ContactsClient, DriveClient, SCOPE_CONTACTS

auth = GoogleAuthManager(
    client_secrets_file="client_secret.json",
    scopes=[*ContactsClient.scopes, *DriveClient.scopes, SCOPE_CONTACTS],
)

# First call opens the browser; subsequent calls use the cached token for "me@gmail.com"
creds = auth.get_credentials(account_key="me@gmail.com")
```

### Forgetting a Token
If you need to force re-authentication for an account:
```python
auth.forget("me@gmail.com")
```

## 2. ServiceAccountAuthManager (Zero-Interaction)

Use `ServiceAccountAuthManager` when every account you need to access belongs to a Workspace domain you administer. This requires domain-wide delegation to be enabled by a super admin.

### How it works:
This manager impersonates users in your organization without requiring any browser interaction or consent screen. No token caching is needed because a fresh, short-lived token is generated on every call.

### Setup:
1. Create a service account in Google Cloud Console and download the JSON key.
2. Enable domain-wide delegation for the service account.
3. In Google Workspace Admin console, authorize the client ID for the necessary scopes.

### Usage Example:
```python
from selander_bridge import ServiceAccountAuthManager

auth = ServiceAccountAuthManager(
    service_account_file="service_account.json",
    scopes=["https://www.googleapis.com/auth/drive"]
)

# Impersonates the user without any browser prompt
creds = auth.get_credentials(subject="employee@yourdomain.com")
```

## Token Storage

By default, cached tokens from `GoogleAuthManager` are stored as JSON files under `~/.selander_bridge/tokens/` (one file per `account_key`).

You can customize this by implementing your own `TokenStore` (e.g., to store tokens in a database or system keyring) and passing it to the `GoogleAuthManager` constructor.
