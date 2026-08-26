from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Profile(BaseModel):
    id: UUID
    name: str
    home_timezone: str
    last_known_timezone: str
    last_timezone_sync_at: datetime
