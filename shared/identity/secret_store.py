"""
Secret Store — OS Keyring Integration for Sovereign Authority

Ported from med_safety_gym/identity/secret_store.py.
Uses macOS Keychain (or system keyring) to store CA keys securely.
Falls back to InMemorySecretStore for CI/testing.
"""
from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Try to import keyring; fall back gracefully
try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False
    logger.warning("keyring package not installed. Using InMemorySecretStore fallback.")


class SecretStore(ABC):
    """Abstract interface for storing agent secrets."""
    
    KNOWN_KEYS = (
        "ca_private_key",
        "ca_public_key",
        "auth_token",
        "hub_pub_key",
    )

    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def set_secret(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def clear_secrets(self) -> None:
        pass


class KeyringSecretStore(SecretStore):
    """Production implementation using OS keyring (e.g. macOS Keychain)."""
    
    SERVICE_NAME = "sovereign_swarm"

    def get_secret(self, key: str) -> Optional[str]:
        if not HAS_KEYRING:
            return None
        try:
            return keyring.get_password(self.SERVICE_NAME, key)
        except Exception as e:
            logger.warning(f"Keyring read failed for '{key}': {e}")
            return None

    def set_secret(self, key: str, value: str) -> None:
        if not HAS_KEYRING:
            logger.warning(f"No keyring backend. Secret '{key}' not saved.")
            return
        try:
            keyring.set_password(self.SERVICE_NAME, key, value)
        except Exception as e:
            logger.warning(f"Keyring write failed for '{key}': {e}")

    def clear_secrets(self) -> None:
        if not HAS_KEYRING:
            return
        for key in self.KNOWN_KEYS:
            try:
                keyring.delete_password(self.SERVICE_NAME, key)
            except Exception:
                pass


class InMemorySecretStore(SecretStore):
    """Ephemeral storage for testing/CI."""
    
    def __init__(self):
        self._secrets = {}

    def get_secret(self, key: str) -> Optional[str]:
        return self._secrets.get(key)

    def set_secret(self, key: str, value: str) -> None:
        self._secrets[key] = value

    def clear_secrets(self) -> None:
        self._secrets.clear()


def get_default_store() -> SecretStore:
    """Returns the best available SecretStore for the current environment."""
    if HAS_KEYRING:
        return KeyringSecretStore()
    return InMemorySecretStore()
