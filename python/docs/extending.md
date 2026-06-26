# Extending selander_bridge

One of the main strengths of `selander_bridge` is its extensible architecture. Every Google API wrapper in this library follows the same basic shape, inheriting from `BaseService`.

Adding support for other Workspace APIs (like Google Calendar, Google Sheets, or Gmail) is straightforward and requires minimal boilerplate.

## 1. Create a New Client Class

To add a new API, create a new Python file or add a class that inherits from `BaseService`. You need to define the `api_name`, `api_version`, and default `scopes`.

Here is an example for the **Google Calendar API**:

```python
from selander_bridge.base import BaseService, wrap_http_errors

class CalendarClient(BaseService):
    api_name = "calendar"
    api_version = "v3"
    scopes = ("https://www.googleapis.com/auth/calendar.readonly",)

    @wrap_http_errors
    def list_events(self, calendar_id="primary", max_results=50):
        """
        self.service lazily initializes the googleapiclient Resource object 
        upon first access.
        """
        resp = self.service.events().list(
            calendarId=calendar_id, 
            maxResults=max_results
        ).execute()
        return resp.get("items", [])
```

## 2. Using the `@wrap_http_errors` Decorator

Notice the `@wrap_http_errors` decorator on the `list_events` method. This decorator catches any raw `HttpError` exceptions thrown by `googleapiclient` and re-raises them as a `SelanderBridgeError`. 

Always use this decorator on public methods interacting with `self.service` to maintain a consistent exception hierarchy across the library.

## 3. Expose Your New Client

If you are modifying the `selander_bridge` package directly, remember to export your new client in `src/selander_bridge/__init__.py`:

```python
# In src/selander_bridge/__init__.py
from .calendar import CalendarClient

__all__ = [
    # ... existing exports ...
    "CalendarClient",
]
```

## 4. Include Necessary Scopes

When initializing the `GoogleAuthManager`, ensure you include the scopes required by your new client:

```python
from selander_bridge import GoogleAuthManager

# Assuming CalendarClient is defined or imported
auth = GoogleAuthManager(
    client_secrets_file="client_secret.json",
    scopes=[*CalendarClient.scopes] 
)

calendar = CalendarClient(auth, account="me@gmail.com")
events = calendar.list_events()
```
