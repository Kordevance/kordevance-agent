from pydantic import BaseModel


class SaveDeviceDetailsRequest(BaseModel):
    device_id: str
    device_secret: str
