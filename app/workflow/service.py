from typing import Any
from app.agents.local import LocalPlanningAgent, LocalRepositoryAgent, LocalRequirementAgent, LocalReviewAgent
from app.schemas import Artifact, WorkflowCreate, WorkflowRun, WorkflowStatus
from app.storage.repository import WorkflowRepository
from app.workflow.engine import transition


class WorkflowService:
    def __init__(self, repository: WorkflowRepository):
        self.repository = repository
        self.requirement_agent = LocalRequirementAgent()
        self.repository_agent = LocalRepositoryAgent()
        self.planning_agent = LocalPlanningAgent()
        self.review_agent = LocalReviewAgent()

    def create_and_run(self, request: WorkflowCreate) -> WorkflowRun:
        workflow = WorkflowRun(
            title=request.title, description=request.description,
            repository_url=str(request.repository_url) if request.repository_url else None,
            constraints=request.constraints, requested_by=request.requested_by,
        )
        self.repository.save_workflow(workflow)
        context: dict[str, Any] = {}
        try:
            transition(workflow, WorkflowStatus.CLARIFYING, "requirement_analysis")
            self.repository.save_workflow(workflow)
            spec = self.requirement_agent.build_spec(workflow)
            self.repository.save_spec(workflow.id, spec)
            context["requirement_spec"] = spec.model_dump(mode="json")
            self._artifact(workflow, "requirement_spec", "结构化需求规格", context["requirement_spec"])

            transition(workflow, WorkflowStatus.SPEC_READY, "requirement_spec_ready")
            self.repository.save_workflow(workflow)
            transition(workflow, WorkflowStatus.ANALYZING_REPOSITORY, "repository_analysis")
            report = self.repository_agent.run(workflow, context)
            context["repository_analysis"] = report
            self._artifact(workflow, "repository_analysis", "仓库分析报告", report)
            self.repository.save_workflow(workflow)

            transition(workflow, WorkflowStatus.PLANNING, "technical_planning")
            plan = self.planning_agent.run(workflow, context)
            context["technical_plan"] = plan
            self._artifact(workflow, "technical_plan", "技术方案与任务拆分", plan)
            self.repository.save_workflow(workflow)

            transition(workflow, WorkflowStatus.REVIEWING, "quality_review")
            review = self.review_agent.run(workflow, context)
            self._artifact(workflow, "quality_review", "质量门禁报告", review)
            target = WorkflowStatus.BLOCKED if review["blocking_questions"] else WorkflowStatus.COMPLETED
            stage = "blocked_on_questions" if target == WorkflowStatus.BLOCKED else "mvp_delivered"
            transition(workflow, target, stage)
            self.repository.save_workflow(workflow)
            return workflow
        except Exception:
            if workflow.status not in {WorkflowStatus.COMPLETED, WorkflowStatus.FAILED}:
                try:
                    transition(workflow, WorkflowStatus.FAILED, "failed")
                except ValueError:
                    workflow.status = WorkflowStatus.FAILED
            self.repository.save_workflow(workflow)
            raise

    def _artifact(self, workflow: WorkflowRun, kind: str, title: str, content: dict[str, Any]):
        self.repository.save_artifact(Artifact(
            workflow_id=workflow.id, kind=kind, title=title, content=content
        ))
