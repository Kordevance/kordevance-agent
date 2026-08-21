from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from kordevance.domain.models.llm_provider import AuthorizedLLMProviders
from kordevance.domain.ports.model_catalog_client import ModelCatalogClient
from kordevance.exceptions import BadRequestError


@dataclass(frozen=True)
class _ProviderCatalogSpec:
    path: str
    headers: Callable[[str], dict[str, str]]
    params: Callable[[str], dict[str, str]]
    parse: Callable[[dict[str, Any]], list[str]]


def _bearer_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _no_params(_: str) -> dict[str, str]:
    return {}


def _parse_openai_style(payload: dict[str, Any]) -> list[str]:
    return [str(entry["id"]) for entry in payload.get("data", [])]


def _parse_anthropic(payload: dict[str, Any]) -> list[str]:
    return [str(entry["id"]) for entry in payload.get("data", [])]


def _parse_gemini(payload: dict[str, Any]) -> list[str]:
    return [str(entry["name"]).removeprefix("models/") for entry in payload.get("models", [])]


_PROVIDER_CATALOG_SPECS: dict[AuthorizedLLMProviders, _ProviderCatalogSpec] = {
    AuthorizedLLMProviders.OpenAI: _ProviderCatalogSpec(
        path="/models", headers=_bearer_headers, params=_no_params, parse=_parse_openai_style
    ),
    AuthorizedLLMProviders.DeepSeek: _ProviderCatalogSpec(
        path="/models", headers=_bearer_headers, params=_no_params, parse=_parse_openai_style
    ),
    AuthorizedLLMProviders.OpenRouter: _ProviderCatalogSpec(
        path="/models", headers=_bearer_headers, params=_no_params, parse=_parse_openai_style
    ),
    AuthorizedLLMProviders.XAI: _ProviderCatalogSpec(
        path="/v1/models", headers=_bearer_headers, params=_no_params, parse=_parse_openai_style
    ),
    AuthorizedLLMProviders.Mistral: _ProviderCatalogSpec(
        path="/v1/models", headers=_bearer_headers, params=_no_params, parse=_parse_openai_style
    ),
    AuthorizedLLMProviders.Anthropic: _ProviderCatalogSpec(
        path="/v1/models",
        headers=lambda api_key: {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        params=_no_params,
        parse=_parse_anthropic,
    ),
    AuthorizedLLMProviders.Gemini: _ProviderCatalogSpec(
        path="/v1beta/models",
        headers=lambda api_key: {"x-goog-api-key": api_key},
        params=_no_params,
        parse=_parse_gemini,
    ),
}


class HttpModelCatalogClient(ModelCatalogClient):
    """Fetches the live list of sub-models a provider exposes via its /models-style endpoint."""

    async def list_models(self, provider: AuthorizedLLMProviders, endpoint: str, api_key: str) -> list[str]:
        spec = _PROVIDER_CATALOG_SPECS.get(provider)
        if spec is None:
            raise BadRequestError(f"No model catalog is available for provider: {provider}")

        url = endpoint.rstrip("/") + spec.path
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=spec.headers(api_key), params=spec.params(api_key))
            response.raise_for_status()
            return spec.parse(response.json())
