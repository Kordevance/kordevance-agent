from datetime import datetime

from pydantic import BaseModel


class DeviceRegistration(BaseModel):
    device_id: str
    registered_at: datetime
