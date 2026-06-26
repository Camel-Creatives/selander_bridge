"""Wrapper around the Google People API (Contacts)."""
from __future__ import annotations

from typing import Any, Iterator, Optional

from .base import BaseService, wrap_http_errors

# Read-only is the safer default. Write operations need the full "contacts"
# scope, so callers can opt in only when they need CRUD.
SCOPE_CONTACTS_READONLY = "https://www.googleapis.com/auth/contacts.readonly"
SCOPE_CONTACTS = "https://www.googleapis.com/auth/contacts"

DEFAULT_PERSON_FIELDS = "names,emailAddresses,phoneNumbers,organizations"


class ContactsClient(BaseService):
    """
    Example:
        contacts = ContactsClient(auth, account="me@gmail.com")
        for person in contacts.list_contacts():
            print(person.get("names"))

    By default this client is read-only. To use create/update/delete methods,
    include `SCOPE_CONTACTS` in the auth manager's scope list.
    """

    api_name = "people"
    api_version = "v1"
    scopes = (SCOPE_CONTACTS_READONLY,)

    @wrap_http_errors
    def list_contacts(
        self,
        page_size: int = 100,
        person_fields: str = DEFAULT_PERSON_FIELDS,
    ) -> Iterator[dict]:
        """Yield every contact connection for the authenticated user, handling pagination."""
        request = self.service.people().connections().list(
            resourceName="people/me",
            pageSize=page_size,
            personFields=person_fields,
        )
        while request is not None:
            response = request.execute()
            yield from response.get("connections", [])
            request = self.service.people().connections().list_next(request, response)

    @wrap_http_errors
    def get_contact(
        self, resource_name: str, person_fields: str = DEFAULT_PERSON_FIELDS
    ) -> dict:
        """resource_name looks like 'people/c1234567890123456789'."""
        return (
            self.service.people()
            .get(resourceName=resource_name, personFields=person_fields)
            .execute()
        )

    @wrap_http_errors
    def search_contacts(self, query: str, page_size: int = 10) -> Iterator[dict]:
        """
        Search the authenticated user's "other contacts" + contacts by name,
        nickname, email, or phone number substring.
        """
        response = (
            self.service.people()
            .searchContacts(query=query, pageSize=page_size, readMask=DEFAULT_PERSON_FIELDS)
            .execute()
        )
        for result in response.get("results", []):
            yield result.get("person", {})

    @wrap_http_errors
    def create_contact(
        self,
        *,
        body: Optional[dict[str, Any]] = None,
        given_name: Optional[str] = None,
        family_name: str = "",
        email: Optional[str] = None,
    ) -> dict:
        """
        Create a new contact.

        You can pass a raw People API `body`, or use the simple name/email
        helpers for common cases.
        """
        if body is None:
            if not given_name:
                raise ValueError("Either body or given_name must be provided")
            body = {"names": [{"givenName": given_name, "familyName": family_name}]}
            if email:
                body["emailAddresses"] = [{"value": email}]
        return self.service.people().createContact(body=body).execute()

    @wrap_http_errors
    def update_contact(
        self,
        resource_name: str,
        *,
        body: dict[str, Any],
        update_person_fields: str,
    ) -> dict:
        """
        Update an existing contact.

        `update_person_fields` should be a comma-separated field mask such as
        "names,emailAddresses".
        """
        return (
            self.service.people()
            .updateContact(
                resourceName=resource_name,
                updatePersonFields=update_person_fields,
                body=body,
            )
            .execute()
        )

    @wrap_http_errors
    def delete_contact(self, resource_name: str) -> None:
        """Delete a contact by People API resource name."""
        self.service.people().deleteContact(resourceName=resource_name).execute()
