from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PairingInvite(BaseModel):
    id: UUID
    code_hash: str
    expires_at: datetime
    created_at: datetime
