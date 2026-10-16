from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_workflow_and_artifacts():
    response = client.post("/api/v1/workflows", json={
        "title": "Add CSV export",
        "description": "Allow administrators to export filtered user records as CSV.",
        "repository_url": "https://github.com/example/demo",
        "constraints": ["Never export passwords or access tokens"],
        "requested_by": "test",
    })
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "completed"
    detail = client.get(f"/api/v1/workflows/{payload['id']}")
    assert detail.status_code == 200
    assert detail.json()["requirement_spec"]["title"] == "Add CSV export"
    assert len(detail.json()["artifacts"]) >= 4


def test_missing_repository_blocks():
    response = client.post("/api/v1/workflows", json={
        "title": "Improve report",
        "description": "Improve the report page and make its filters easier to use.",
        "requested_by": "test",
    })
    assert response.status_code == 201
    assert response.json()["status"] == "blocked"
