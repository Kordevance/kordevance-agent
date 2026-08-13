from typing import Annotated

from fastapi import Depends

from kordevance.application.dependencies.sql_store_adapter import ModelAssignmentDep, ModelProviderDep
from kordevance.domain.use_cases.model_assignment_management.handle_delete_assignment import (
    HandleDeleteModelAssignment,
)
from kordevance.domain.use_cases.model_assignment_management.handle_fetch_assignments import (
    HandleFetchModelAssignments,
)
from kordevance.domain.use_cases.model_assignment_management.handle_set_assignment import HandleSetModelAssignment


def get_set_model_assignment_use_case(
    repository: ModelAssignmentDep, provider_repository: ModelProviderDep
) -> HandleSetModelAssignment:
    return HandleSetModelAssignment(repository=repository, provider_repository=provider_repository)


def get_delete_model_assignment_use_case(repository: ModelAssignmentDep) -> HandleDeleteModelAssignment:
    return HandleDeleteModelAssignment(repository=repository)


def get_fetch_model_assignments_use_case(repository: ModelAssignmentDep) -> HandleFetchModelAssignments:
    return HandleFetchModelAssignments(repository=repository)


SetModelAssignmentUseCaseDep = Annotated[HandleSetModelAssignment, Depends(get_set_model_assignment_use_case)]
DeleteModelAssignmentUseCaseDep = Annotated[HandleDeleteModelAssignment, Depends(get_delete_model_assignment_use_case)]
GetModelAssignmentsUseCaseDep = Annotated[HandleFetchModelAssignments, Depends(get_fetch_model_assignments_use_case)]
