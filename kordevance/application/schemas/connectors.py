from pydantic import BaseModel


class GetConnectorsResponse(BaseModel):
    provider: str
    category: str
    active: bool
