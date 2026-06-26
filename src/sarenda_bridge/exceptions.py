"""Exceptions raised by sarenda_bridge."""


class SarendaBridgeError(Exception):
    """Base class for every error raised by this library."""


class AuthenticationError(SarendaBridgeError):
    """Raised when acquiring or refreshing Google credentials fails."""


class MissingClientSecretsError(SarendaBridgeError):
    """Raised when no client_secrets file/dict was supplied and none can be found."""
