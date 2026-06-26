"""Wrapper around the Google Drive API."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional, Union

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from .base import BaseService, wrap_http_errors

SCOPE_DRIVE_READONLY = "https://www.googleapis.com/auth/drive.readonly"
SCOPE_DRIVE_FILE = "https://www.googleapis.com/auth/drive.file"  # files the app created/opened
SCOPE_DRIVE = "https://www.googleapis.com/auth/drive"  # full access

DEFAULT_FIELDS = "nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink)"


class DriveClient(BaseService):
    """
    Example:
        drive = DriveClient(auth, account="me@gmail.com")
        for f in drive.list_files(query="mimeType='application/pdf'"):
            print(f["name"])
    """

    api_name = "drive"
    api_version = "v3"
    scopes = (SCOPE_DRIVE,)

    @wrap_http_errors
    def list_files(
        self,
        query: Optional[str] = None,
        page_size: int = 100,
        fields: str = DEFAULT_FIELDS,
    ) -> Iterator[dict]:
        """Yield files matching an optional Drive query string, handling pagination."""
        page_token = None
        while True:
            response = (
                self.service.files()
                .list(q=query, pageSize=page_size, fields=fields, pageToken=page_token)
                .execute()
            )
            yield from response.get("files", [])
            page_token = response.get("nextPageToken")
            if not page_token:
                break

    @wrap_http_errors
    def upload_file(
        self,
        local_path: Union[str, Path],
        parent_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> dict:
        local_path = Path(local_path)
        metadata: dict = {"name": name or local_path.name}
        if parent_id:
            metadata["parents"] = [parent_id]
        media = MediaFileUpload(str(local_path), resumable=True)
        return (
            self.service.files()
            .create(body=metadata, media_body=media, fields="id, name, webViewLink")
            .execute()
        )

    @wrap_http_errors
    def download_file(self, file_id: str, destination: Union[str, Path]) -> Path:
        destination = Path(destination)
        request = self.service.files().get_media(fileId=file_id)
        with destination.open("wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        return destination

    @wrap_http_errors
    def create_folder(self, name: str, parent_id: Optional[str] = None) -> dict:
        metadata: dict = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            metadata["parents"] = [parent_id]
        return self.service.files().create(body=metadata, fields="id, name").execute()

    @wrap_http_errors
    def delete_file(self, file_id: str) -> None:
        self.service.files().delete(fileId=file_id).execute()

    @wrap_http_errors
    def share_file(self, file_id: str, email: str, role: str = "reader") -> dict:
        """role: 'reader', 'commenter', or 'writer'."""
        permission = {"type": "user", "role": role, "emailAddress": email}
        return (
            self.service.permissions()
            .create(fileId=file_id, body=permission, fields="id")
            .execute()
        )
