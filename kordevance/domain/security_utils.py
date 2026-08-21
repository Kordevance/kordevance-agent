import hashlib
import secrets


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_device_token() -> str:
    return secrets.token_urlsafe(32)


def generate_pairing_code() -> str:
    return secrets.token_hex(8)
