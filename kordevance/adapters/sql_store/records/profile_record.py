from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ProfileRecord(SQLModel, table=True):
    __tablename__ = "profiles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
