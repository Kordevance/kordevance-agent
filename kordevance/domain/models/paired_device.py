from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PairedDevice(BaseModel):
    id: UUID
    is_owner: bool
    created_at: datetime
