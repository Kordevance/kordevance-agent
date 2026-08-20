from uuid import UUID

from pydantic import BaseModel


class ConnectorRequest(BaseModel):
    profile_id: UUID
    provider: str
    category: str
