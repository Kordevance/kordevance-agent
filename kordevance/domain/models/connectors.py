from pydantic import BaseModel


class Connector(BaseModel):
    provider: str
    category: str
    icon: str = ""
    active: bool


class AvailableConnectors(BaseModel):
    provider: str
    icon: str = ""
    categories: list[str]
