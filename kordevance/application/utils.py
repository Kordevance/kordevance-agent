from uuid import UUID


def parse_id(id: str) -> UUID | None:
    try:
        return UUID(id)
    except ValueError:
        return None
