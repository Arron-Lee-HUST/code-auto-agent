from datetime import datetime, timezone
from app.schemas import WorkflowRun, WorkflowStatus


ALLOWED_TRANSITIONS = {
    WorkflowStatus.CREATED: {WorkflowStatus.CLARIFYING, WorkflowStatus.FAILED},
    WorkflowStatus.CLARIFYING: {WorkflowStatus.SPEC_READY, WorkflowStatus.BLOCKED, WorkflowStatus.FAILED},
    WorkflowStatus.SPEC_READY: {WorkflowStatus.ANALYZING_REPOSITORY, WorkflowStatus.FAILED},
    WorkflowStatus.ANALYZING_REPOSITORY: {WorkflowStatus.PLANNING, WorkflowStatus.FAILED},
    WorkflowStatus.PLANNING: {WorkflowStatus.REVIEWING, WorkflowStatus.FAILED},
    WorkflowStatus.REVIEWING: {WorkflowStatus.BLOCKED, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED},
    WorkflowStatus.BLOCKED: {WorkflowStatus.CLARIFYING, WorkflowStatus.FAILED},
    WorkflowStatus.COMPLETED: set(),
    WorkflowStatus.FAILED: set(),
}


class InvalidTransition(ValueError):
    pass


def transition(workflow: WorkflowRun, target: WorkflowStatus, stage: str) -> WorkflowRun:
    if target not in ALLOWED_TRANSITIONS.get(workflow.status, set()):
        raise InvalidTransition(f"Transition not allowed: {workflow.status} -> {target}")
    workflow.status = target
    workflow.current_stage = stage
    workflow.updated_at = datetime.now(timezone.utc)
    return workflow
