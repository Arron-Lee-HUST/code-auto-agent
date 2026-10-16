# API 文档

默认地址 `http://127.0.0.1:8000`；Swagger UI：`/docs`。

- `GET /health`：服务健康状态。
- `POST /api/v1/workflows`：创建并运行工作流。
- `GET /api/v1/workflows?limit=50`：列出最近工作流，limit 为 1–200。
- `GET /api/v1/workflows/{workflow_id}`：返回工作流、需求规格和产物。
- `GET /api/v1/workflows/{workflow_id}/spec`：返回结构化需求规格。
- `GET /api/v1/workflows/{workflow_id}/artifacts`：返回产物列表。

创建请求示例：
```json
{
  "title": "增加用户导出功能",
  "description": "管理员可以将筛选后的用户导出为 CSV。",
  "repository_url": "https://github.com/example/project",
  "constraints": ["不得导出密码或令牌"],
  "requested_by": "product"
}
```

常见状态码：422 请求校验失败；404 资源不存在；500 工作流执行失败（内部细节不会返回给客户端）。
