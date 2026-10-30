"""R1 FastAPI adapter. Legacy server.py is preserved and remains separate."""
import os
import hmac
from time import perf_counter
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from .schemas import RunRequest, HealthResponse, ErrorResponse
from agentmesh.core import Mesh,Task
from agentmesh.constraints import nonempty,contains
from agentmesh.observability import analyze_run
from agentmesh.event_journal import EventJournal
from agentmesh.security_policy import Principal, Policy, SlidingWindowLimiter
from agentmesh.r8_telemetry import RunTelemetry

def require_token(authorization: str | None = Header(default=None)):
    token=os.getenv("AGENTMESH_API_TOKEN","")
    if token and not hmac.compare_digest(authorization or "", "Bearer "+token):
        raise HTTPException(status_code=401,detail="unauthorized")

def configured_journal():
    path=os.getenv("AGENTMESH_DB_PATH","")
    return EventJournal(path) if path else None

def create_app():
    app=FastAPI(title="AgentMesh Optional API",version="0.2.0")
    @app.middleware("http")
    async def secure_response_headers(request,call_next):
        response=await call_next(request)
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["Referrer-Policy"]="no-referrer"
        response.headers["X-Frame-Options"]="DENY"
        response.headers["Cache-Control"]="no-store"
        return response
    limiter=SlidingWindowLimiter(limit=int(os.getenv("AGENTMESH_R9_RATE_LIMIT","30")))
    telemetry=RunTelemetry()
    def require_execution_policy(authorization: str | None = Header(default=None)):
        require_token(authorization)
        if os.getenv("AGENTMESH_R9_ENFORCE")!="1":return
        if not os.getenv("AGENTMESH_API_TOKEN"):
            raise HTTPException(503,"r9_requires_token")
        principal=Principal("configured-api-token","operator")
        if not Policy().allowed(principal,"runs:execute"):
            raise HTTPException(403,"permission_denied")
        if not limiter.accept(principal.identifier):
            raise HTTPException(429,"rate_limit_exceeded")
    @app.get("/")
    def index():
        return {"service":"AgentMesh optional FastAPI","documentation":"/docs","health":"/api/health","run":"/api/v2/run","legacy_dashboard":"Use server.py on port 8000"}
    @app.get("/api/health",response_model=HealthResponse)
    def health():
        return HealthResponse()
    @app.post("/api/v2/run",dependencies=[Depends(require_execution_policy)])
    def run(payload: RunRequest):
        started=perf_counter()
        constraints=[nonempty()]
        if payload.contains:constraints.append(contains(payload.contains))
        result=Mesh(max_attempts=payload.attempts).run(Task(payload.objective,constraints)).to_dict()
        result["observability"]=analyze_run({**result,"mode":"agents"})
        journal=configured_journal()
        if journal:
            result["run_id"]=journal.record(result)
        result["telemetry"]=telemetry.record(accepted=result["accepted"],
            duration_ms=(perf_counter()-started)*1000,run_id=result.get("run_id"),
            event_count=len(result.get("trace",[])))
        return result
    @app.get("/api/v2/telemetry",dependencies=[Depends(require_token)])
    def telemetry_snapshot(limit: int=30):
        if not 1<=limit<=100:raise HTTPException(400,"invalid_limit")
        return telemetry.snapshot(limit)
    @app.get("/api/v2/runs",dependencies=[Depends(require_token)])
    def runs(limit: int=30):
        if not 1<=limit<=100:raise HTTPException(400,"invalid_limit")
        journal=configured_journal()
        if journal is None:raise HTTPException(503,"storage_disabled")
        return {"runs":journal.list_runs(limit)}
    @app.get("/api/v2/runs/{run_id}",dependencies=[Depends(require_token)])
    def run_detail(run_id: str):
        journal=configured_journal()
        if journal is None:raise HTTPException(503,"storage_disabled")
        result=journal.get_run(run_id)
        if result is None:raise HTTPException(404,"run_not_found")
        return result
    @app.get("/api/v2/runs/{run_id}/events",dependencies=[Depends(require_token)])
    def run_events(run_id: str,after: int=0,limit: int=100):
        if not 0<=after or not 1<=limit<=500:raise HTTPException(400,"invalid_cursor")
        journal=configured_journal()
        if journal is None:raise HTTPException(503,"storage_disabled")
        if journal.get_run(run_id) is None:raise HTTPException(404,"run_not_found")
        return {"run_id":run_id,"events":journal.events(run_id,after,limit)}
    @app.exception_handler(HTTPException)
    async def http_error(request,exc):
        return JSONResponse(status_code=exc.status_code,content={"error":str(exc.detail)})
    return app

app=create_app()
