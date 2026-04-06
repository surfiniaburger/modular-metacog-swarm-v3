"""
SafeClaw Crypto Layer — ED25519 Signatures

Provides small, focused functions for manifest signing and verification.
Follows Farley practices: functions < 10 lines, clear communication.
"""
import logging
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)


def generate_keys():
    """Generate a new ED25519 private/public key pair."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def export_private_key(private_key: ed25519.Ed25519PrivateKey) -> bytes:
    """Serialize private key to PKCS8 PEM format (compatible with PyJWT)."""
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


def export_public_key(public_key: ed25519.Ed25519PublicKey) -> bytes:
    """Serialize public key to PEM format."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def load_private_key(pem_data: bytes) -> ed25519.Ed25519PrivateKey:
    """Load a private key from PEM bytes."""
    return serialization.load_pem_private_key(pem_data, password=None)


def load_public_key(pem_data: bytes) -> ed25519.Ed25519PublicKey:
    """Load a public key from PEM bytes."""
    return serialization.load_pem_public_key(pem_data)


def sign_data(data: bytes, private_key: ed25519.Ed25519PrivateKey) -> bytes:
    """Sign raw bytes with an ED25519 private key."""
    return private_key.sign(data)


def verify_signature(data: bytes, signature: bytes, public_key: ed25519.Ed25519PublicKey) -> bool:
    """Verify an ED25519 signature."""
    try:
        public_key.verify(signature, data)
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        logger.error(f"Crypto verification error: {e}")
        return False
