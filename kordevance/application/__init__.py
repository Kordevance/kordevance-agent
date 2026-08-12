from pathlib import Path

_WORKING_DIRECTORY: Path = Path.home().joinpath(".kordevance")
_WORKING_DIRECTORY.mkdir(exist_ok=True, parents=True)
