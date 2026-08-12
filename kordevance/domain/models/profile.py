from uuid import UUID

from pydantic import BaseModel


class Profile(BaseModel):
    id: UUID
    name: str
