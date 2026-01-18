"""Encryption utilities for sensitive data like API keys"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from .config import settings


def _get_fernet() -> Fernet:
    """Create a Fernet instance using the app's secret key"""
    # Derive a 32-byte key from the secret key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"studybuddy_salt",  # Static salt (secret_key provides entropy)
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode()))
    return Fernet(key)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage"""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage"""
    fernet = _get_fernet()
    decrypted = fernet.decrypt(encrypted_key.encode())
    return decrypted.decode()
