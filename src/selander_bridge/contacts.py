"""Wrapper around the Google People API (Contacts)."""
from __future__ import annotations

from typing import Iterator, Optional

from .base import BaseService, wrap_http_errors

# Read-only is the safer default; switch to the full "contacts" scope
# if your app also needs to create/update contacts.
SCOPE_CONTACTS_READONLY = "https://www.googleapis.com/auth/contacts.readonly"
SCOPE_CONTACTS = "https://www.googleapis.com/auth/contacts"

DEFAULT_PERSON_FIELDS = "names,emailAddresses,phoneNumbers,organizations"


class ContactsClient(BaseService):
    """
    Example:
        contacts = ContactsClient(auth, account="me@gmail.com")
        for person in contacts.list_contacts():
            print(person.get("names"))
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
    def create_contact(self, *, given_name: str, family_name: str = "", email: Optional[str] = None) -> dict:
        """Requires the full SCOPE_CONTACTS scope, not just readonly."""
        body: dict = {"names": [{"givenName": given_name, "familyName": family_name}]}
        if email:
            body["emailAddresses"] = [{"value": email}]
        return self.service.people().createContact(body=body).execute()
