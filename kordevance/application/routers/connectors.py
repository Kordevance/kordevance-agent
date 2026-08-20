from uuid import UUID

from fastapi import APIRouter, Depends

from kordevance.application.dependencies.connectors_management import FetchConnectorsUseCaseDep
from kordevance.application.dependencies.deps import get_profile_id
from kordevance.application.schemas.connectors import GetConnectorsResponse

router: APIRouter = APIRouter(prefix="/connectors", tags=["connectors"])


@router.get("", response_model=list[GetConnectorsResponse])
async def get_all_connectors(
    service: FetchConnectorsUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> list[GetConnectorsResponse]:
    connectors = await service.execute(profile_id)
    return [
        GetConnectorsResponse(provider=connector.provider, category=connector.category, active=connector.active)
        for connector in connectors
    ]
