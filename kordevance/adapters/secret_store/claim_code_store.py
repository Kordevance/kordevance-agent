import secrets
from pathlib import Path

from kordevance.domain.ports.claim_code_store import ClaimCodeStore


class FileClaimCodeStore(ClaimCodeStore):
    def __init__(self, path: Path) -> None:
        self._path: Path = path

    def get_or_create(self) -> str:
        if self._path.exists():
            return self._path.read_text().strip()

        code = secrets.token_hex(8)
        self._path.write_text(code)
        self._path.chmod(0o600)
        return code

    def invalidate(self) -> None:
        self._path.unlink(missing_ok=True)
