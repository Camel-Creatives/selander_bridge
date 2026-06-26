# Selander Bridge Documentation

Welcome to the documentation for **selander_bridge**, a reusable Python library designed to bridge your applications to Google accounts and Google Workspace services (such as Drive and Contacts).

## Overview

The primary goal of `selander_bridge` is to provide a seamless way to authenticate with Google APIs without the need to host a permanent web server to handle OAuth redirects. It is built to be imported everywhere, making it ideal for desktop applications, local scripts, and administrative tools.

It defaults to Google's **installed-app / loopback flow**, capturing the redirect on a temporary local port and caching the refresh token to disk. It also supports **Service Accounts** for zero-interaction, domain-wide delegation.

## Features

- **No Server Hosting Required:** Uses loopback OAuth flow to eliminate the need for a persistent redirect URI endpoint.
- **Token Caching:** Refresh tokens are securely cached to disk per account, skipping the login screen for subsequent executions.
- **Service Account Support:** Seamless integration for Google Workspace administrators to act on behalf of users via domain-wide delegation.
- **Built-in Service Clients:**
  - **Contacts API:** List, search, create, update, and delete contacts.
  - **Drive API:** List, upload, download, share files, and create folders.
- **Extensible Architecture:** Designed to easily add wrappers for other Google Workspace APIs like Calendar, Sheets, or Gmail.

## Getting Started

Check out the following guides to start using `selander_bridge`:

1. **[Authentication Guide](auth.md)**: Learn how to configure OAuth and Service Account authentication.
2. **[Contacts API Guide](contacts.md)**: Manage Google Contacts.
3. **[Drive API Guide](drive.md)**: Manage files and folders in Google Drive.
4. **[Extending the Library](extending.md)**: Learn how to add support for more Google Workspace APIs.
