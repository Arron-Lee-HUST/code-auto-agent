import sqlite3
from pathlib import Path
from threading import RLock
from app.schemas import Artifact, RequirementSpec, WorkflowRun


class WorkflowRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self._lock = RLock()
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.database_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self):
        with self._lock, self._connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS workflows (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            conn.execute("CREATE TABLE IF NOT EXISTS specs (workflow_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            conn.execute("CREATE TABLE IF NOT EXISTS artifacts (id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, payload TEXT NOT NULL)")

    def save_workflow(self, item: WorkflowRun):
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO workflows VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                (item.id, item.model_dump_json()),
            )

    def get_workflow(self, workflow_id: str):
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT payload FROM workflows WHERE id=?", (workflow_id,)).fetchone()
        return WorkflowRun.model_validate_json(row["payload"]) if row else None

    def list_workflows(self, limit: int = 50):
        with self._lock, self._connect() as conn:
            rows = conn.execute("SELECT payload FROM workflows ORDER BY rowid DESC LIMIT ?", (limit,)).fetchall()
        return [WorkflowRun.model_validate_json(row["payload"]) for row in rows]

    def save_spec(self, workflow_id: str, spec: RequirementSpec):
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO specs VALUES (?, ?) ON CONFLICT(workflow_id) DO UPDATE SET payload=excluded.payload",
                (workflow_id, spec.model_dump_json()),
            )

    def get_spec(self, workflow_id: str):
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT payload FROM specs WHERE workflow_id=?", (workflow_id,)).fetchone()
        return RequirementSpec.model_validate_json(row["payload"]) if row else None

    def save_artifact(self, artifact: Artifact):
        with self._lock, self._connect() as conn:
            conn.execute("INSERT INTO artifacts VALUES (?, ?, ?)",
                         (artifact.id, artifact.workflow_id, artifact.model_dump_json()))

    def list_artifacts(self, workflow_id: str):
        with self._lock, self._connect() as conn:
            rows = conn.execute("SELECT payload FROM artifacts WHERE workflow_id=? ORDER BY rowid",
                                (workflow_id,)).fetchall()
        return [Artifact.model_validate_json(row["payload"]) for row in rows]
