from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class PairedDeviceRecord(SQLModel, table=True):
    __tablename__ = "paired_devices"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token_hash: str = Field(index=True, unique=True)
    is_owner: bool = False
    created_at: datetime
