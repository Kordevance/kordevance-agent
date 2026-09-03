from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Index, text
from sqlmodel import Field, SQLModel


class PairedDeviceRecord(SQLModel, table=True):
    __tablename__ = "paired_devices"
    __table_args__ = (
        Index("ux_paired_devices_bootstrap", "is_bootstrap", unique=True, sqlite_where=text("is_bootstrap = 1")),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token_hash: str = Field(index=True, unique=True)
    is_owner: bool = False
    is_bootstrap: bool = False
    created_at: datetime
