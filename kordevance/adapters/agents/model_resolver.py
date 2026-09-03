from uuid import UUID

from pydantic_ai.models import Model

from kordevance.domain.models.llm_provider import AuthorizedLLMProviders, LLMProvider
from kordevance.domain.models.model_assignment import ModelAssignment
from kordevance.domain.models.model_role import ModelRole
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo
from kordevance.exceptions import ItemNotFoundError


def _build_model(provider: LLMProvider, model_id: str) -> Model:  # noqa: C901
    match provider.name:
        case AuthorizedLLMProviders.Anthropic:
            from pydantic_ai.models.anthropic import AnthropicModel
            from pydantic_ai.providers.anthropic import AnthropicProvider

            return AnthropicModel(
                model_id, provider=AnthropicProvider(api_key=provider.api_key, base_url=provider.endpoint)
            )

        case AuthorizedLLMProviders.OpenAI:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider

            return OpenAIChatModel(
                model_id, provider=OpenAIProvider(api_key=provider.api_key, base_url=provider.endpoint)
            )

        case AuthorizedLLMProviders.DeepSeek:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider

            return OpenAIChatModel(
                model_id, provider=OpenAIProvider(api_key=provider.api_key, base_url=provider.endpoint)
            )

        case AuthorizedLLMProviders.OpenRouter:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider

            return OpenAIChatModel(
                model_id, provider=OpenAIProvider(api_key=provider.api_key, base_url=provider.endpoint)
            )

        case AuthorizedLLMProviders.Gemini:
            from pydantic_ai.models.google import GoogleModel
            from pydantic_ai.providers.google import GoogleProvider

            return GoogleModel(model_id, provider=GoogleProvider(api_key=provider.api_key))

        case AuthorizedLLMProviders.Mistral:
            from pydantic_ai.models.mistral import MistralModel
            from pydantic_ai.providers.mistral import MistralProvider

            return MistralModel(model_id, provider=MistralProvider(api_key=provider.api_key))

        case AuthorizedLLMProviders.XAI:
            from pydantic_ai.models.xai import XaiModel
            from pydantic_ai.providers.xai import XaiProvider

            return XaiModel(model_id, provider=XaiProvider(api_key=provider.api_key))

        case AuthorizedLLMProviders.Other:
            from pydantic_ai.models.openai import OpenAIChatModel
            from pydantic_ai.providers.openai import OpenAIProvider

            return OpenAIChatModel(
                model_id,
                provider=OpenAIProvider(api_key=provider.api_key or "not-needed", base_url=provider.endpoint),
            )

        case _:
            raise ValueError(f"No pydantic-ai model mapping for provider: {provider.name}")


class ModelResolver:
    def __init__(self, model_assignment_repo: ModelAssignmentRepo, llm_provider_repo: LLMProviderRepo) -> None:
        self._model_assignment_repo: ModelAssignmentRepo = model_assignment_repo
        self._llm_provider_repo: LLMProviderRepo = llm_provider_repo

    async def resolve(self, profile_id: UUID, role: ModelRole) -> Model:
        assignment = await self._resolve_assignment(profile_id, role)
        provider = await self._llm_provider_repo.fetch(profile_id, assignment.provider_id)
        return _build_model(provider, assignment.model_id)

    async def _resolve_assignment(self, profile_id: UUID, role: ModelRole) -> ModelAssignment:
        if role == ModelRole.PRIMARY:
            return await self._model_assignment_repo.fetch(profile_id, role)

        try:
            return await self._model_assignment_repo.fetch(profile_id, role)
        except ItemNotFoundError:
            return await self._model_assignment_repo.fetch(profile_id, ModelRole.PRIMARY)
