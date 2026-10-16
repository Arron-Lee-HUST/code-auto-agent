from abc import ABC, abstractmethod
from typing import Any
from app.schemas import RequirementSpec, WorkflowRun


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, workflow: WorkflowRun, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class RequirementAgent(BaseAgent):
    @abstractmethod
    def build_spec(self, workflow: WorkflowRun) -> RequirementSpec:
        raise NotImplementedError
