from uuid import UUID


def parse_id(entity_id: str) -> UUID | None:
    try:
        return UUID(entity_id)
    except ValueError:
        return None
