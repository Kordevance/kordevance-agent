from collections.abc import Callable
from pathlib import Path


def load_or_create_text(path: Path, generate: Callable[[], str]) -> str:
    if path.exists():
        return path.read_text().strip()

    value = generate()
    path.write_text(value)
    path.chmod(0o600)
    return value


def load_or_create_bytes(path: Path, generate: Callable[[], bytes]) -> bytes:
    if path.exists():
        return path.read_bytes()

    value = generate()
    path.write_bytes(value)
    path.chmod(0o600)
    return value
