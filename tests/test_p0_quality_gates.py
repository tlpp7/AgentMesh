"""Q01-Q09 defensive regression contracts; no external browser dependencies."""
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]

def test_baseline_reports_unknown_when_not_measured(tmp_path):
    output=tmp_path/"baseline.json"
    p=subprocess.run([sys.executable,str(ROOT/"scripts/quality_baseline.py"),"--output",str(output)],cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    report=json.loads(output.read_text())
    assert all(c["status"]=="UNKNOWN" for c in report["checks"].values())
    assert all(v=="UNKNOWN" for v in report["standards"].values())

def test_accessible_graph_alternative_and_navigation():
    html=(ROOT/"apps/web-v2/index.html").read_text()
    ui=(ROOT/"apps/web-v2/src/main.tsx").read_text()
    css=(ROOT/"apps/web-v2/src/dashboard.css").read_text()
    assert 'lang="fr"' in html
    assert "Aller au contenu principal" in ui
    assert 'aria-pressed={selected===name}' in ui
    assert 'role="status"' in ui
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css

def test_agent_tool_scopes_enforced(monkeypatch):
    import agentmesh.tool_supervisor as supervisor
    invoked=[]
    monkeypatch.setattr(supervisor,"invoke_tool",lambda name,args:invoked.append(name) or {"status":"ok","tool":name})
    steps=[{"tool":"evaluate_trace","arguments":{}},{"tool":"review_issue","arguments":{}}]
    result=supervisor.run_tool_plan(steps,agent="analyzer")
    assert result["steps"][0]["status"]=="ok"
    assert result["steps"][1]["status"]=="denied"
    assert invoked==["evaluate_trace"]
    result=supervisor.run_tool_plan(steps,agent="unknown")
    assert result["executed"]==0

def test_api_security_headers(monkeypatch):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from apps.api.main import create_app
    client=TestClient(create_app())
    r=client.get("/api/health")
    assert r.status_code==200
    assert r.headers["x-content-type-options"]=="nosniff"
    assert r.headers["referrer-policy"]=="no-referrer"
    assert r.headers["x-frame-options"]=="DENY"
    assert r.headers["cache-control"]=="no-store"
