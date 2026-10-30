"""R1 FastAPI adapter. Legacy server.py is preserved and remains separate."""
import os
import hmac
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from .schemas import RunRequest, HealthResponse, ErrorResponse
from agentmesh.core import Mesh,Task
from agentmesh.constraints import nonempty,contains
from agentmesh.observability import analyze_run

def require_token(authorization: str | None = Header(default=None)):
    token=os.getenv("AGENTMESH_API_TOKEN","")
    if token and not hmac.compare_digest(authorization or "", "Bearer "+token):
        raise HTTPException(status_code=401,detail="unauthorized")

def create_app():
    app=FastAPI(title="AgentMesh Optional API",version="0.2.0")
    @app.get("/")
    def index():
        return {"service":"AgentMesh optional FastAPI","documentation":"/docs","health":"/api/health","run":"/api/v2/run","legacy_dashboard":"Use server.py on port 8000"}
    @app.get("/api/health",response_model=HealthResponse)
    def health():
        return HealthResponse()
    @app.post("/api/v2/run",dependencies=[Depends(require_token)])
    def run(payload: RunRequest):
        constraints=[nonempty()]
        if payload.contains:constraints.append(contains(payload.contains))
        result=Mesh(max_attempts=payload.attempts).run(Task(payload.objective,constraints)).to_dict()
        result["observability"]=analyze_run({**result,"mode":"agents"})
        return result
    @app.exception_handler(HTTPException)
    async def http_error(request,exc):
        return JSONResponse(status_code=exc.status_code,content={"error":str(exc.detail)})
    return app

app=create_app()
