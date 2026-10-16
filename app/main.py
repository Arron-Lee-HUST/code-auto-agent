from fastapi import FastAPI, HTTPException, Query
from app.config import get_settings
from app.schemas import Artifact, HealthResponse, RequirementSpec, WorkflowCreate, WorkflowDetail, WorkflowRun
from app.storage.repository import WorkflowRepository
from app.workflow.service import WorkflowService

settings = get_settings()
repository = WorkflowRepository(settings.database_path)
service = WorkflowService(repository)
app = FastAPI(title=settings.app_name, version="0.1.0",
              description="Workflow-first multi-agent software delivery MVP")


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    return HealthResponse()


@app.post("/api/v1/workflows", response_model=WorkflowRun, status_code=201, tags=["workflows"])
def create_workflow(request: WorkflowCreate):
    try:
        return service.create_and_run(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Workflow execution failed") from exc


@app.get("/api/v1/workflows", response_model=list[WorkflowRun], tags=["workflows"])
def list_workflows(limit: int = Query(default=50, ge=1, le=200)):
    return repository.list_workflows(limit)


@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowDetail, tags=["workflows"])
def get_workflow(workflow_id: str):
    workflow = repository.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowDetail(workflow=workflow, requirement_spec=repository.get_spec(workflow_id),
                          artifacts=repository.list_artifacts(workflow_id))


@app.get("/api/v1/workflows/{workflow_id}/spec", response_model=RequirementSpec, tags=["artifacts"])
def get_spec(workflow_id: str):
    if not repository.get_workflow(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    spec = repository.get_spec(workflow_id)
    if not spec:
        raise HTTPException(status_code=404, detail="Requirement spec not found")
    return spec


@app.get("/api/v1/workflows/{workflow_id}/artifacts", response_model=list[Artifact], tags=["artifacts"])
def get_artifacts(workflow_id: str):
    if not repository.get_workflow(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return repository.list_artifacts(workflow_id)
