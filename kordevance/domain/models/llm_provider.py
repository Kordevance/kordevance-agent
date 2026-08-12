from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuthorizedLLMProviders(StrEnum):
    DeepSeek = "deep-seek"
    Anthropic = "anthropic"
    OpenRouter = "open-router"
    OpenAI = "open-ai"
    Gemini = "gemini"
    Mistral = "mistral"
    XAI = "xai"


class LLMProvider(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: AuthorizedLLMProviders
    endpoint: str
    tokens_used: int
