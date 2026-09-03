from datetime import datetime

from sqlmodel import Field, SQLModel


class DeviceRegistrationRecord(SQLModel, table=True):
    __tablename__ = "device_registration"

    # Singleton row: one installation, at most one registration record.
    id: int = Field(default=1, primary_key=True)
    device_id: str
    registered_at: datetime
