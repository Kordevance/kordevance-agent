from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    reason: str
