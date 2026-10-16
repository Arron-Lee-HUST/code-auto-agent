# 工作流与 Agent 契约

| Agent | 输入 | 输出 | 禁止事项 |
|---|---|---|---|
| Requirement | 需求与约束 | RequirementSpec | 不把猜测当事实 |
| Repository Analysis | 仓库元信息、只读索引 | 目录/依赖/测试入口报告 | 不执行仓库脚本 |
| Planning | Spec 与仓库报告 | 设计决策、任务 DAG、风险 | 不绕过审批写代码 |
| Coding（后续） | 已批准任务、隔离工作副本 | 代码差异和测试结果 | 不访问生产密钥 |
| QA（后续） | Spec、代码差异 | 测试计划、结果、覆盖缺口 | 不仅凭 Agent 自述通过 |
| Review | Spec、计划、测试产物 | 门禁结论和阻塞项 | 不自批高风险发布 |
| Delivery（后续） | 已验证 PR/制品 | PR、部署和回滚记录 | 生产发布需审批 |
| Knowledge（后续） | 已验证结果 | 可检索经验条目 | 不把未验证建议写成事实 |

## 状态机
`app/workflow/engine.py` 中的 `ALLOWED_TRANSITIONS` 管理合法迁移。Agent 不应直接改状态；必须通过工作流服务迁移。

## Artifact
每个产物包含 `id`、`workflow_id`、`kind`、`title`、`content`、`created_at`。生产版建议添加 schema_version、producer_agent、输入产物 ID、模型/提示词版本、内容 hash 和审批记录。

## 可靠性
当前为同步 MVP，不支持崩溃恢复。生产版需持久化检查点、队列、超时、有限重试、取消、人工接管和幂等键。Git 写入、PR、部署等步骤恢复前必须查询外部状态。
