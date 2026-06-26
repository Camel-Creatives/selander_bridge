"""Exceptions raised by selander_bridge."""


class SelanderBridgeError(Exception):
    """Base class for every error raised by this library."""


class AuthenticationError(SelanderBridgeError):
    """Raised when acquiring or refreshing Google credentials fails."""


class MissingClientSecretsError(SelanderBridgeError):
    """Raised when no client_secrets file/dict was supplied and none can be found."""
