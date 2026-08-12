import logging

from kordevance.application import _WORKING_DIRECTORY


def setup_logging() -> None:
    filename = _WORKING_DIRECTORY.joinpath("app.log")

    logging.basicConfig(
        level=logging.INFO,
        filename=filename,
        format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filemode="a",
    )
