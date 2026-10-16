from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowStatus(StrEnum):
    CREATED = "created"
    CLARIFYING = "clarifying"
    SPEC_READY = "spec_ready"
    ANALYZING_REPOSITORY = "analyzing_repository"
    PLANNING = "planning"
    REVIEWING = "reviewing"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class AcceptanceCriterion(BaseModel):
    id: str = Field(default_factory=lambda: f"AC-{uuid4().hex[:8]}")
    given: str = Field(min_length=1)
    when: str = Field(min_length=1)
    then: str = Field(min_length=1)


class NonFunctionalRequirement(BaseModel):
    category: str
    requirement: str


class RequirementSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    goal: str
    actors: list[str] = Field(default_factory=list)
    scope_in: list[str] = Field(default_factory=list)
    scope_out: list[str] = Field(default_factory=list)
    business_rules: list[str] = Field(default_factory=list)
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)
    non_functional_requirements: list[NonFunctionalRequirement] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    assumptions: list[str] = Field(default_factory=list)


class WorkflowCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=20000)
    repository_url: HttpUrl | None = None
    constraints: list[str] = Field(default_factory=list)
    requested_by: str = Field(default="anonymous", max_length=200)


class Artifact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    kind: str
    title: str
    content: dict[str, Any]
    created_at: datetime = Field(default_factory=utc_now)


class WorkflowRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    repository_url: str | None = None
    constraints: list[str] = Field(default_factory=list)
    requested_by: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_stage: str = "created"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    error: str | None = None


class WorkflowDetail(BaseModel):
    workflow: WorkflowRun
    requirement_spec: RequirementSpec | None = None
    artifacts: list[Artifact] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "code-auto-agent"
