from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class PairingInviteRecord(SQLModel, table=True):
    __tablename__ = "pairing_invites"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    code_hash: str
    expires_at: datetime
    created_at: datetime
