# 系统架构

## 原则
- Workflow-first：状态迁移由普通代码控制，不由 LLM 决定。
- Schema-first：Agent 输入输出通过 Pydantic 校验。
- Artifact-first：每个阶段产生可追踪产物。
- Least privilege：工具按最小权限授予，读仓库与写仓库分开。
- Human-in-the-loop：生产发布和不可逆操作需要审批。
- Provider isolation：模型、Git、数据库和执行器通过适配层接入。

## 当前逻辑架构
```text
Client -> FastAPI -> WorkflowService -> Workflow Engine
                                  |-> Requirement Agent
                                  |-> Repository Analysis Agent
                                  |-> Planning Agent
                                  |-> Quality Review Agent
                                  `-> SQLite Workflow/Artifact Repository
```

## 生产目标架构
- Web：React + TypeScript。
- API：FastAPI + Pydantic。
- 持久化编排：Temporal 或 LangGraph，初期选择一个。
- 数据：PostgreSQL；Redis 用于缓存/短期协调。
- 仓库解析：Git provider、ripgrep、Tree-sitter、依赖清单。
- 执行：隔离容器/微虚拟机，网络默认关闭，限制资源和运行时长。
- 交付：GitHub/GitLab provider、CI、PR、临时测试环境。
- 可观测性：workflow_id、agent_run_id、tool_call_id、artifact_id。

## 状态与一致性
当前状态：created → clarifying → spec_ready → analyzing_repository → planning → reviewing → completed；存在开放问题则进入 blocked，异常进入 failed。
SQLite 适合单进程开发。生产需 PostgreSQL 事务、持久化检查点、有限重试、取消、人工接管和幂等键。外部操作必须查询状态和对账，不假设恰好执行一次。

## 模型路由
Agent 业务逻辑与模型适配器分离。按任务选择模型，并记录模型、提示词版本、token、延迟、成本和输出校验结果。当前不包含真实模型路由。
