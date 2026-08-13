import logging

from kordevance.application import _WORKING_DIRECTORY


def setup_logging() -> None:
    filename = _WORKING_DIRECTORY.joinpath("app.log")

    formatter = logging.Formatter(
        fmt="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(filename, mode="a")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True
    )
