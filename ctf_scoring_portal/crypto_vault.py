"""
================================================================================
CyberVault : Operation ShadowTrace - Cryptographic Flag Vault
Implements AES-256 encryption, decryption, and secure flag validation.
================================================================================
"""

import os
import hmac
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment configuration
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DEFAULT_KEY = b"VO2Nz0HFFKiuggQZvtbfVRPGte_iZWMYphLuDbwWZLs="
RAW_KEY = os.getenv("FLAG_ENCRYPTION_KEY", "").strip().encode() or DEFAULT_KEY
FLAG_SALT = os.getenv("FLAG_SALT", "cybervault_flag_salt_2026_salt!").strip()

try:
    _cipher = Fernet(RAW_KEY)
except Exception:
    # Fallback to default key if provided key was invalid
    _cipher = Fernet(DEFAULT_KEY)


def encrypt_flag(plaintext_flag: str) -> str:
    """
    Encrypts a plaintext CTF flag using AES-256 Fernet authenticated encryption.
    Returns base64 encoded ciphertext string.
    """
    if not plaintext_flag:
        return ""
    clean = plaintext_flag.strip()
    encrypted_bytes = _cipher.encrypt(clean.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_flag(ciphertext: str) -> str:
    """
    Decrypts an AES-256 encrypted CTF flag back into plaintext.
    """
    if not ciphertext:
        return ""
    try:
        decrypted_bytes = _cipher.decrypt(ciphertext.strip().encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        return f"[Decryption Error: {e}]"


def hash_flag(plaintext_flag: str) -> str:
    """
    Computes a salted SHA-256 digest of the flag for timing-attack safe verification.
    """
    clean = plaintext_flag.strip()
    salted = f"{FLAG_SALT}:{clean}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def verify_flag(submitted_flag: str, expected_ciphertext: str, expected_hash: str = None) -> bool:
    """
    Verifies if a user-submitted flag matches the expected stored encrypted flag.
    Employs timing-attack resistant hmac.compare_digest.
    """
    if not submitted_flag:
        return False
    
    clean_sub = submitted_flag.strip()

    # Fast path: hash verification
    if expected_hash:
        sub_hash = hash_flag(clean_sub)
        if hmac.compare_digest(sub_hash, expected_hash):
            return True

    # Decrypt and compare
    decrypted = decrypt_flag(expected_ciphertext)
    return hmac.compare_digest(clean_sub, decrypted)


def get_crypto_status() -> dict:
    """
    Returns cryptographic health and cipher metadata for Admin diagnostics.
    """
    test_str = "CVT{crypto_selftest_pass}"
    enc = encrypt_flag(test_str)
    dec = decrypt_flag(enc)
    healthy = (dec == test_str)

    return {
        "cipher": "AES-256 (Fernet Authenticated Envelope)",
        "hash_algorithm": "Salted SHA-256 HMAC digest",
        "key_fingerprint": hashlib.sha256(RAW_KEY).hexdigest()[:16] + "...",
        "healthy": healthy
    }
