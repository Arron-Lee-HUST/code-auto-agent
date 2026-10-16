import pytest
from app.schemas import WorkflowRun, WorkflowStatus
from app.workflow.engine import InvalidTransition, transition


def test_valid_transition_updates_stage():
    item = WorkflowRun(title="Demo", description="A detailed test request", requested_by="test")
    transition(item, WorkflowStatus.CLARIFYING, "requirements")
    assert item.status == WorkflowStatus.CLARIFYING
    assert item.current_stage == "requirements"


def test_invalid_transition_is_rejected():
    item = WorkflowRun(title="Demo", description="A detailed test request", requested_by="test")
    with pytest.raises(InvalidTransition):
        transition(item, WorkflowStatus.COMPLETED, "done")
