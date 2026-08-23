import re
from typing import Any
from uuid import UUID

from pydantic_ai import RunContext
from pydantic_ai.tools import Tool

from kordevance.domain.models.device import Device
from kordevance.domain.models.tool import ToolDefinition
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient

_INVALID_TOOL_NAME_CHARS = re.compile(r"[^a-zA-Z0-9_-]")


def sanitize_tool_name(name: str) -> str:
    return _INVALID_TOOL_NAME_CHARS.sub("_", name)[:128]


def build_callable_tool(
    tool_def: ToolDefinition,
    profile_id: UUID,
    device: Device,
    proxy_relay_client: ProxyRelayClient,
    used_names: set[str],
) -> Tool[Any]:
    async def _call(_ctx: RunContext[Any], **kwargs: Any) -> Any:
        return await proxy_relay_client.execute_tool(device, profile_id, tool_def.name, dict(kwargs))

    name = sanitize_tool_name(tool_def.name)
    if name in used_names:
        suffix = 2
        while f"{name}_{suffix}" in used_names:
            suffix += 1
        name = f"{name}_{suffix}"
    used_names.add(name)

    return Tool.from_schema(
        function=_call,
        name=name,
        description=tool_def.description,
        json_schema=tool_def.input_schema,
        takes_ctx=True,
    )


def build_callable_tools(
    tool_defs: list[ToolDefinition],
    profile_id: UUID,
    device: Device,
    proxy_relay_client: ProxyRelayClient,
) -> list[Tool[Any]]:
    used_names: set[str] = set()
    return [
        build_callable_tool(t, profile_id, device, proxy_relay_client, used_names)
        for t in tool_defs
        if not t.requires_confirmation
    ]
