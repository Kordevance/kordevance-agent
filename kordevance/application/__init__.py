import os
from pathlib import Path

from kordevance import _APPLICATION_NAME

# Every file this process creates is born owner-only
os.umask(0o077)

_WORKING_DIRECTORY: Path = Path.home().joinpath(f".{_APPLICATION_NAME}")


_WORKING_DIRECTORY.mkdir(exist_ok=True, parents=True, mode=0o700)
_WORKING_DIRECTORY.chmod(0o700)  # rwx
