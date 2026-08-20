from typing import Any

from pydantic import BaseModel


class ToolDefinition(BaseModel):
    """A tool exposed by ProxyRelay for a given provider/category, already scoped to the calling
    device profile's live connections. A tool only appears here once its provider/category has
    an active connection. input_schema is the tool's JSON Schema for its input payload, passed
    through as-is so an agent can build a call against it without needing to know each
    tool's shape ahead of time.
    """

    name: str
    description: str
    provider: str
    category: str
    requires_confirmation: bool
    input_schema: dict[str, Any]
