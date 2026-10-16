from typing import Any
from app.agents.base import BaseAgent, RequirementAgent
from app.schemas import (
    AcceptanceCriterion, NonFunctionalRequirement, RequirementSpec, RiskLevel, WorkflowRun,
)


class LocalRequirementAgent(RequirementAgent):
    name = "requirement"

    def build_spec(self, workflow: WorkflowRun) -> RequirementSpec:
        text = workflow.description.strip()
        risk_terms = ("payment", "production", "delete all", "支付", "生产", "删除", "权限")
        risk = RiskLevel.HIGH if any(term in text.lower() for term in risk_terms) else RiskLevel.MEDIUM
        questions = []
        if not workflow.repository_url:
            questions.append("目标代码仓库是什么？未提供 repository_url。")
        if not workflow.constraints:
            questions.append("是否存在兼容性、性能、安全、发布时间或技术栈约束？")
        return RequirementSpec(
            title=workflow.title,
            goal=text,
            actors=["需求提出者", "最终用户（待确认）"],
            scope_in=[text],
            scope_out=["未经明确授权的生产发布", "未经审批的破坏性数据操作"],
            business_rules=workflow.constraints,
            acceptance_criteria=[
                AcceptanceCriterion(
                    given="需求已提交", when="工作流生成需求规格",
                    then="系统输出目标、范围、风险和验收标准",
                ),
                AcceptanceCriterion(
                    given="需求存在未确认信息", when="系统生成需求规格",
                    then="未确认事项被记录为开放问题而不是事实",
                ),
            ],
            non_functional_requirements=[
                NonFunctionalRequirement(category="security", requirement="工具调用遵循最小权限"),
                NonFunctionalRequirement(category="traceability", requirement="阶段产物关联 workflow_id"),
            ],
            open_questions=questions,
            risk_level=risk,
            assumptions=["当前为本地演示 Agent；业务方确认后才能视为最终需求"],
        )

    def run(self, workflow: WorkflowRun, context: dict[str, Any]) -> dict[str, Any]:
        return self.build_spec(workflow).model_dump(mode="json")


class LocalRepositoryAgent(BaseAgent):
    name = "repository_analysis"

    def run(self, workflow: WorkflowRun, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "repository_url": workflow.repository_url,
            "analysis_mode": "metadata_only",
            "findings": [
                "MVP 不会自动克隆仓库或执行仓库代码。",
                "真实分析应在受控沙箱内进行，并将仓库内容视为不可信输入。",
            ],
            "recommended_next_step": "实现只读 Git provider，分析目录树、依赖与测试入口。",
        }


class LocalPlanningAgent(BaseAgent):
    name = "technical_planning"

    def run(self, workflow: WorkflowRun, context: dict[str, Any]) -> dict[str, Any]:
        spec = context.get("requirement_spec", {})
        return {
            "goal": spec.get("goal", workflow.description),
            "design_principles": [
                "业务规则与基础设施适配器解耦",
                "先定义契约和验收标准，再拆分任务",
                "高风险副作用通过权限策略和人工审批",
            ],
            "implementation_tasks": [
                {"id": "TASK-1", "title": "定义领域模型与接口契约", "depends_on": []},
                {"id": "TASK-2", "title": "实现核心业务逻辑", "depends_on": ["TASK-1"]},
                {"id": "TASK-3", "title": "添加单元测试与边界用例", "depends_on": ["TASK-1", "TASK-2"]},
                {"id": "TASK-4", "title": "运行质量门禁并生成交付记录", "depends_on": ["TASK-3"]},
            ],
            "approval_required": True,
            "approval_reason": "方案需负责人确认后才能授权真实代码写入或外部副作用。",
        }


class LocalReviewAgent(BaseAgent):
    name = "quality_review"

    def run(self, workflow: WorkflowRun, context: dict[str, Any]) -> dict[str, Any]:
        spec = context.get("requirement_spec", {})
        questions = spec.get("open_questions", [])
        return {
            "result": "needs_clarification" if questions else "passed_with_mvp_limits",
            "checks": [
                {"name": "structured_requirement", "passed": bool(spec), "detail": "需求规格存在"},
                {"name": "open_questions_visible", "passed": True, "detail": f"未决问题数：{len(questions)}"},
                {"name": "unsafe_side_effects_disabled", "passed": True, "detail": "Git 写入和部署默认关闭"},
            ],
            "blocking_questions": questions,
            "note": "该检查不替代真实代码测试、安全扫描或人工评审。",
        }
