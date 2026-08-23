from uuid import UUID

from fastapi import APIRouter, Depends, status

from kordevance.application.dependencies.auth import require_paired_device
from kordevance.application.dependencies.deps import get_profile_id
from kordevance.application.dependencies.model_catalog import FetchModelCatalogUseCaseDep
from kordevance.application.dependencies.model_provider_management import (
    AddProviderUseCaseDep,
    DeleteProviderUseCaseDep,
    GetProvidersUseCaseDep,
    GetProviderUseCaseDep,
)
from kordevance.application.schemas.model_provider import ModelProviderRequest, ModelProviderResponse
from kordevance.domain.use_cases.llm_provider_management.request_models import (
    AddProviderRequest,
    GenericProviderRequest,
)

router: APIRouter = APIRouter(prefix="/providers", tags=["providers"], dependencies=[Depends(require_paired_device)])


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_provider(
    body: ModelProviderRequest, service: AddProviderUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> ModelProviderResponse:
    payload = AddProviderRequest(
        profile_id=profile_id,
        name=body.name,
        api_key=body.api_key,
        endpoint=body.endpoint,
        display_name=body.display_name,
    )
    provider = await service.execute(payload)
    return ModelProviderResponse.from_domain(provider)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    id: UUID, service: DeleteProviderUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> None:
    return await service.execute(GenericProviderRequest(profile_id=profile_id, provider_id=id))


@router.get("/{id}")
async def get_provider(
    id: UUID, service: GetProviderUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> ModelProviderResponse:
    provider = await service.execute(GenericProviderRequest(profile_id=profile_id, provider_id=id))
    return ModelProviderResponse.from_domain(provider)


@router.get("")
async def get_all_providers(
    service: GetProvidersUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> list[ModelProviderResponse]:
    providers = await service.execute(profile_id)
    return [ModelProviderResponse.from_domain(provider) for provider in providers]


@router.get("/{id}/models")
async def get_provider_model_catalog(
    id: UUID, service: FetchModelCatalogUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> list[str]:
    return await service.execute(GenericProviderRequest(profile_id=profile_id, provider_id=id))
