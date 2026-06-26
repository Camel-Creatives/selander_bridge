# Google Drive API

The `DriveClient` provides a wrapper around the Google Drive API to manage files and folders.

## Import
```python
from selander_bridge import DriveClient, SCOPE_DRIVE, SCOPE_DRIVE_READONLY, SCOPE_DRIVE_FILE
```

## Scopes
- `SCOPE_DRIVE` (`https://www.googleapis.com/auth/drive`): Full access to Drive. This is the default scope requested by the client.
- `SCOPE_DRIVE_READONLY` (`https://www.googleapis.com/auth/drive.readonly`): Read-only access to file metadata and content.
- `SCOPE_DRIVE_FILE` (`https://www.googleapis.com/auth/drive.file`): Access to files created or opened by the app.

## Initialization
```python
# Assuming 'auth' is an initialized GoogleAuthManager or ServiceAccountAuthManager
drive = DriveClient(auth, account="user@gmail.com")
```

## Methods

### `list_files`
Yields files matching an optional Drive query string. Automatically handles pagination.

```python
# List all PDF files
for f in drive.list_files(query="mimeType='application/pdf'"):
    print(f"Found PDF: {f['name']} (ID: {f['id']})")
```

### `upload_file`
Uploads a local file to Google Drive. Supports resumable uploads.
Optionally, specify a `parent_id` to upload into a specific folder, or `name` to override the filename.

```python
uploaded_file = drive.upload_file(
    local_path="/path/to/report.pdf",
    name="Q2 Report.pdf",
    parent_id="folder_id_here"
)
print(f"View file: {uploaded_file.get('webViewLink')}")
```

### `download_file`
Downloads a file from Google Drive to the local filesystem.

```python
downloaded_path = drive.download_file(
    file_id="drive_file_id_here",
    destination="/local/path/to/save/report.pdf"
)
print(f"Downloaded to {downloaded_path}")
```

### `create_folder`
Creates a new folder in Google Drive. Optionally, pass `parent_id` to nest it inside another folder.

```python
folder = drive.create_folder(name="Project Assets", parent_id="parent_folder_id")
print(f"Created folder ID: {folder['id']}")
```

### `delete_file`
Deletes a file or folder by its ID.

```python
drive.delete_file(file_id="drive_file_id_here")
```

### `share_file`
Shares a file with a specific email address and assigns a role. Roles can be `'reader'`, `'commenter'`, or `'writer'`.

```python
permission = drive.share_file(
    file_id="drive_file_id_here",
    email="colleague@example.com",
    role="writer"
)
```
