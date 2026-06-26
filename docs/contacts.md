# Google Contacts API

The `ContactsClient` provides a simple wrapper around the Google People API to manage contacts.

## Import
```python
from selander_bridge import ContactsClient, SCOPE_CONTACTS, SCOPE_CONTACTS_READONLY
```

## Scopes
- `SCOPE_CONTACTS_READONLY` (`https://www.googleapis.com/auth/contacts.readonly`): Used for `list_contacts`, `get_contact`, and `search_contacts`. This is the default scope requested by the client.
- `SCOPE_CONTACTS` (`https://www.googleapis.com/auth/contacts`): Required if you want to use the write operations (`create_contact`, `update_contact`, `delete_contact`). You must explicitly include this scope in your `GoogleAuthManager` initialization.

## Initialization
```python
# Assuming 'auth' is an initialized GoogleAuthManager or ServiceAccountAuthManager
contacts = ContactsClient(auth, account="user@gmail.com")
```

## Methods

### `list_contacts`
Yields every contact connection for the authenticated user. Automatically handles pagination.

```python
for person in contacts.list_contacts():
    names = person.get("names", [])
    if names:
        print(f"Name: {names[0].get('displayName')}")
```

### `get_contact`
Retrieves a specific contact by its resource name.

```python
resource_name = "people/c1234567890"
person = contacts.get_contact(resource_name)
print(person)
```

### `search_contacts`
Searches the user's "other contacts" and contacts by name, nickname, email, or phone number substring.

```python
for result in contacts.search_contacts(query="John"):
    print(result.get("names"))
```

### `create_contact`
Creates a new contact. You can use the helper arguments (`given_name`, `family_name`, `email`) for simple creation, or pass a raw Google People API `body` dictionary for complex contacts.

**Requires `SCOPE_CONTACTS`**.

```python
# Simple creation
new_contact = contacts.create_contact(
    given_name="Ada",
    family_name="Lovelace",
    email="ada@example.com"
)

# Using raw body
new_contact = contacts.create_contact(
    body={
        "names": [{"givenName": "Alan", "familyName": "Turing"}],
        "organizations": [{"name": "Bletchley Park"}]
    }
)
```

### `update_contact`
Updates an existing contact. You must provide the fields to update via the `update_person_fields` mask.

**Requires `SCOPE_CONTACTS`**.

```python
contacts.update_contact(
    resource_name=new_contact["resourceName"],
    body={"names": [{"givenName": "Ada", "familyName": "Byron"}]},
    update_person_fields="names"
)
```

### `delete_contact`
Deletes a contact by its resource name.

**Requires `SCOPE_CONTACTS`**.

```python
contacts.delete_contact(new_contact["resourceName"])
```
