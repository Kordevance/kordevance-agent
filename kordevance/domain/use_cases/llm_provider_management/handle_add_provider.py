import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.llm_client_factory import LLMProviderFactory
from kordevance.domain.models.llm_provider import LLMProvider
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.use_cases.llm_provider_management.request_models import AddProviderRequest
from kordevance.exceptions import BadRequestError


class HandleAddProvider(UseCase[AddProviderRequest, LLMProvider]):
    def __init__(self, repository: LLMProviderRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: LLMProviderRepo = repository

    async def execute(self, request: AddProviderRequest) -> LLMProvider:
        self._logger.info(f"Adding LLM provider {request.name}")

        provider_type = LLMProviderFactory.parse_provider(request.name)
        if provider_type is None:
            raise BadRequestError(f"Provider {request.name} is not supported")

        try:
            provider = LLMProviderFactory.build_client(
                provider=provider_type,
                endpoint=request.endpoint,
                api_key=request.api_key,
                display_name=request.display_name,
            )
        except ValueError as err:
            raise BadRequestError(str(err)) from err

        await self._repository.save(request.profile_id, provider)
        return provider
