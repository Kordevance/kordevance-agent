import os
from pathlib import Path

# Every file this process creates is born owner-only
os.umask(0o077)

_WORKING_DIRECTORY: Path = Path.home().joinpath(".kordevance")


_WORKING_DIRECTORY.mkdir(exist_ok=True, parents=True, mode=0o700)
_WORKING_DIRECTORY.chmod(0o700)  # rwx
