import shutil
from pathlib import Path
from uuid import UUID

from kordevance.domain.ports.profile_workspace import ProfileWorkspace


class LocalProfileWorkspace(ProfileWorkspace):
    def __init__(self, base_dir: Path) -> None:
        self._base_dir: Path = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._base_dir.chmod(0o700)

    def _path(self, profile_id: UUID) -> Path:
        return self._base_dir.joinpath(str(profile_id))

    async def create_profile(self, profile_id: UUID) -> Path:
        return await self.load_profile(profile_id)

    async def delete_profile(self, profile_id: UUID) -> None:
        path = self._path(profile_id)
        if path.exists():
            shutil.rmtree(path)

    async def load_profile(self, profile_id: UUID) -> Path:
        path = self._path(profile_id)
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.chmod(0o700)
        return path

    async def delete_all(self) -> None:
        if self._base_dir.exists():
            shutil.rmtree(self._base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._base_dir.chmod(0o700)
