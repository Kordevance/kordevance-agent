from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RegisterDeviceRequest(BaseModel):
    code: str


class RegisterDeviceResponse(BaseModel):
    token: str


class PairingInviteResponse(BaseModel):
    code: str


class PairedDeviceResponse(BaseModel):
    id: UUID
    is_owner: bool
    created_at: datetime
