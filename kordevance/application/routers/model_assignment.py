from fastapi import APIRouter, Depends, status

from kordevance.application.dependencies.auth import require_paired_device
from kordevance.application.dependencies.deps import get_profile_context
from kordevance.application.dependencies.model_assignment_management import (
    DeleteModelAssignmentUseCaseDep,
    GetModelAssignmentsUseCaseDep,
    SetModelAssignmentUseCaseDep,
)
from kordevance.application.schemas.model_assignment import ModelAssignmentRequest, ModelAssignmentResponse
from kordevance.application.schemas.profile import ProfileContext
from kordevance.domain.models.model_role import ModelRole
from kordevance.domain.use_cases.model_assignment_management.request_models import (
    DeleteModelAssignmentRequest,
    SetModelAssignmentRequest,
)

router: APIRouter = APIRouter(
    prefix="/model-assignments",
    tags=["model-assignments"],
    dependencies=[Depends(require_paired_device), Depends(get_profile_context)],
)


@router.put("/{role}", status_code=status.HTTP_200_OK)
async def set_model_assignment(
    role: ModelRole,
    body: ModelAssignmentRequest,
    service: SetModelAssignmentUseCaseDep,
    profile_context: ProfileContext = Depends(get_profile_context),
) -> ModelAssignmentResponse:
    payload = SetModelAssignmentRequest(
        profile_id=profile_context.profile_id, role=role, provider_id=body.provider_id, model_id=body.model_id
    )
    assignment = await service.execute(payload)
    return ModelAssignmentResponse(
        role=assignment.role, provider_id=assignment.provider_id, model_id=assignment.model_id
    )


@router.delete("/{role}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_assignment(
    role: ModelRole,
    service: DeleteModelAssignmentUseCaseDep,
    profile_context: ProfileContext = Depends(get_profile_context),
) -> None:
    await service.execute(DeleteModelAssignmentRequest(profile_id=profile_context.profile_id, role=role))


@router.get("")
async def get_model_assignments(
    service: GetModelAssignmentsUseCaseDep, profile_context: ProfileContext = Depends(get_profile_context)
) -> list[ModelAssignmentResponse]:
    assignments = await service.execute(profile_context.profile_id)
    return [ModelAssignmentResponse(role=a.role, provider_id=a.provider_id, model_id=a.model_id) for a in assignments]
