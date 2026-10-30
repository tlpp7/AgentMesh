"""Optional FastAPI adapter; original server.py stays unchanged."""
from agentmesh.core import Mesh, Task
from agentmesh.constraints import nonempty

def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise RuntimeError("Install optional extra: pip install -e '.[api]'") from exc
    class RunRequest(BaseModel):
        objective: str = Field(min_length=1,max_length=5000)
        attempts: int = Field(default=3,ge=1,le=10)
    app=FastAPI(title="AgentMesh Optional API",version="0.1.0")
    @app.get("/api/health")
    def health():return {"status":"ok","adapter":"fastapi","legacy_preserved":True}
    @app.post("/api/v2/run")
    def run(payload:RunRequest):
        return Mesh(max_attempts=payload.attempts).run(Task(payload.objective,[nonempty()])).to_dict()
    return app

# For ASGI: uvicorn apps.api.main:app (requires optional dependency)
try:
    from fastapi import FastAPI
except ImportError:
    app=None
else:
    app=create_app()
