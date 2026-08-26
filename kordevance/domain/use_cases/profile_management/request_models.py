from uuid import UUID

from pydantic import BaseModel


class UpdateProfileRequest(BaseModel):
    profile_id: UUID
    name: str
    home_timezone: str


class CreateProfileRequest(BaseModel):
    name: str
    timezone: str
