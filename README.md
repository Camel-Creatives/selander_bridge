# selander_bridge (Monorepo)

This repository contains the `selander_bridge` implementation in multiple languages. It acts as a reusable bridge between your applications and Google Workspace APIs (Drive, Contacts, etc.), designed specifically to avoid forcing you to host a permanent server for OAuth.

## Projects

* **[Python (`selander-bridge`)](python/README.md)**: The Python package implementation. It uses a loopback flow to cache credentials securely on the local machine.
* **[Go (`selander_bridge_go`)](go/)**: The Golang module implementation.
