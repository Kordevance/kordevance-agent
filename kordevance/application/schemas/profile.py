from uuid import UUID

from pydantic import BaseModel


class CreateProfileRequest(BaseModel):
    name: str


class ProfileResponse(BaseModel):
    id: UUID
    name: str


class UpdateProfileRequest(BaseModel):
    id: UUID
    name: str
    home_timezone: str


class ProfileContext(BaseModel):
    profile_id: UUID
    timezone: str
