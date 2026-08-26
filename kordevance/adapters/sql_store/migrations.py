from collections.abc import Callable

from sqlalchemy.engine import Connection

Migration = Callable[[Connection], None]

MIGRATIONS: list[Migration] = []
