# Code Auto Agent

工作流优先的多 Agent 软件交付 MVP：由确定性工作流引擎管理状态，由专业 Agent 生成结构化产物，通过质量门禁和人工审批控制风险。

## 当前能力
- FastAPI REST API 和 OpenAPI 页面
- Pydantic 结构化需求规格、验收标准、风险等级和开放问题
- 确定性工作流状态机
- 需求分析、仓库分析、技术规划、质量审查四类本地演示 Agent
- SQLite 持久化与 artifact 追踪
- pytest 测试和 GitHub Actions CI
- PRD、架构、API、Agent、安全和路线图文档

本版本的 Agent 是可预测的本地实现，不调用真实 LLM，不克隆仓库，不执行 shell，不写 Git，不创建 PR，也不部署生产。真实模型可通过 `app/agents/base.py` 定义的接口接入。

## 快速开始
需要 Python 3.11+：

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/docs。

创建工作流：
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{"title":"增加 CSV 导出","description":"管理员可以将筛选后的用户导出为 CSV。","repository_url":"https://github.com/example/project","constraints":["不得导出密码或令牌"]}'
```

## 结构
```text
app/
  main.py
  schemas.py
  agents/base.py
  agents/local.py
  storage/repository.py
  workflow/engine.py
  workflow/service.py
docs/
tests/
```

SQLite 仅适用于开发和单进程演示。生产化前需要认证授权、PostgreSQL、持久化任务编排、审计、限流、隔离执行器、工具权限策略和人工发布审批。详见 `docs/`。
