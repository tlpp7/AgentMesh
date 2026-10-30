"""R8 observable contract, privacy and auth tests."""
import pytest
from agentmesh.r8_telemetry import RunTelemetry

def test_bounded_private_records():
    t=RunTelemetry(capacity=2)
    for i in range(3):t.record(accepted=i%2==0,duration_ms=i+1,event_count=i)
    data=t.snapshot()
    assert data["count"]==2
    assert data["p95_duration_ms"] is not None
    assert all("objective" not in e and "output" not in e for e in data["runs"])
    assert len({e["trace_id"] for e in data["runs"]})==2

def test_invalid_metrics():
    t=RunTelemetry()
    with pytest.raises(ValueError):t.record(accepted=True,duration_ms=float("nan"))
    with pytest.raises(ValueError):t.record(accepted=True,duration_ms=-1)
    with pytest.raises(ValueError):t.snapshot(101)
    with pytest.raises(ValueError):RunTelemetry(0)

def test_fastapi_correlates_run_and_metrics(tmp_path,monkeypatch):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from apps.api.main import create_app
    monkeypatch.setenv("AGENTMESH_DB_PATH",str(tmp_path/"r8.db"))
    monkeypatch.setenv("AGENTMESH_API_TOKEN","x"*40)
    monkeypatch.delenv("AGENTMESH_R9_ENFORCE",raising=False)
    client=TestClient(create_app())
    headers={"Authorization":"Bearer "+"x"*40}
    assert client.get("/api/v2/telemetry").status_code==401
    assert client.get("/api/v2/telemetry?limit=101",headers=headers).status_code==400
    created=client.post("/api/v2/run",json={"objective":"R8 trace"},headers=headers)
    assert created.status_code==200
    result=created.json()
    telemetry=client.get("/api/v2/telemetry",headers=headers).json()
    assert telemetry["count"]==1
    assert telemetry["runs"][0]["trace_id"]==result["telemetry"]["trace_id"]
    assert telemetry["runs"][0]["run_id"]==result["run_id"]
    assert "R8 trace" not in str(telemetry)
