from pathlib import Path

from kordevance.adapters.secret_store.file_secret import load_or_create_text
from kordevance.domain.ports.claim_code_store import ClaimCodeStore
from kordevance.domain.security_utils import generate_short_token


class FileClaimCodeStore(ClaimCodeStore):
    def __init__(self, path: Path) -> None:
        self._path: Path = path

    def get_or_create(self) -> str:
        return load_or_create_text(self._path, generate_short_token)

    def invalidate(self) -> None:
        self._path.unlink(missing_ok=True)
