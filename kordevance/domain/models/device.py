from pydantic import BaseModel


class Device(BaseModel):
    id: str
    secret: str
