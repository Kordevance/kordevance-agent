from uuid import UUID

from fastapi import APIRouter, Depends, status

from kordevance.application.dependencies.auth import require_paired_device
from kordevance.application.dependencies.deps import get_profile_context
from kordevance.application.dependencies.goal_management import DeleteGoalUseCaseDep, FetchGoalsUseCaseDep
from kordevance.application.schemas.goals import GoalResponse
from kordevance.application.schemas.profile import ProfileContext
from kordevance.domain.use_cases.goal_management.request_models import DeleteGoalRequest

router: APIRouter = APIRouter(
    prefix="/goals", tags=["goals"], dependencies=[Depends(require_paired_device), Depends(get_profile_context)]
)


@router.get("", response_model=list[GoalResponse])
async def get_all_goals(
    service: FetchGoalsUseCaseDep, profile_context: ProfileContext = Depends(get_profile_context)
) -> list[GoalResponse]:
    goals = await service.execute(profile_context.profile_id)
    return [
        GoalResponse(
            id=goal.id,
            title=goal.title,
            description=goal.description,
            start_at=goal.start_at,
            end_at=goal.end_at,
            status=goal.status,
        )
        for goal in goals
    ]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    id: UUID, service: DeleteGoalUseCaseDep, profile_context: ProfileContext = Depends(get_profile_context)
) -> None:
    await service.execute(DeleteGoalRequest(profile_id=profile_context.profile_id, goal_id=id))
