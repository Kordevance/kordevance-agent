from uuid import UUID

from fastapi import APIRouter, Depends

from kordevance.application.dependencies.auth import require_paired_device
from kordevance.application.dependencies.connectors_management import (
    DeleteConnectorsUseCaseDep,
    FetchConnectorsUseCaseDep,
    RegisterConnectorsUseCaseDep,
)
from kordevance.application.dependencies.deps import get_profile_id
from kordevance.application.schemas.connectors import ConnectorRequest, GetConnectorsResponse
from kordevance.domain.use_cases.connectors_management.request_models import ConnectorRequest as Cr

router: APIRouter = APIRouter(prefix="/connectors", tags=["connectors"], dependencies=[Depends(require_paired_device)])


@router.get("", response_model=list[GetConnectorsResponse])
async def get_all_connectors(
    service: FetchConnectorsUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> list[GetConnectorsResponse]:
    connectors = await service.execute(profile_id)
    return [
        GetConnectorsResponse(
            provider=connector.provider, category=connector.category, active=connector.active, icon=connector.icon
        )
        for connector in connectors
    ]


@router.post("/register")
async def register_connector(
    request: ConnectorRequest, service: RegisterConnectorsUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> str:
    payload = Cr(profile_id=profile_id, provider=request.provider, category=request.category)

    return await service.execute(payload)


@router.delete("")
async def delete_connector(
    request: ConnectorRequest, service: DeleteConnectorsUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> None:
    payload = Cr(profile_id=profile_id, provider=request.provider, category=request.category)

    return await service.execute(payload)
