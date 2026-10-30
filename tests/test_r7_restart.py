"""R7 validates persistence across independent API application instances."""
import pytest
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from apps.api.main import create_app

def test_history_survives_api_recreation(tmp_path,monkeypatch):
    monkeypatch.setenv("AGENTMESH_DB_PATH",str(tmp_path/"r7.db"))
    monkeypatch.setenv("AGENTMESH_API_TOKEN","a"*40)
    headers={"Authorization":"Bearer "+"a"*40}
    first=TestClient(create_app())
    response=first.post("/api/v2/run",json={"objective":"Verify persistence"},headers=headers)
    assert response.status_code==200
    identifier=response.json()["run_id"]
    first.close()
    second=TestClient(create_app())
    fetched=second.get("/api/v2/runs/"+identifier,headers=headers)
    assert fetched.status_code==200
    assert fetched.json()["accepted"] is True
    events=second.get("/api/v2/runs/"+identifier+"/events",headers=headers)
    assert events.status_code==200
    assert len(events.json()["events"])>0
    second.close()

def test_history_routes_require_authentication(tmp_path,monkeypatch):
    monkeypatch.setenv("AGENTMESH_DB_PATH",str(tmp_path/"r7.db"))
    monkeypatch.setenv("AGENTMESH_API_TOKEN","b"*40)
    client=TestClient(create_app())
    assert client.get("/api/v2/runs").status_code==401
    assert client.get("/api/v2/runs/missing").status_code==401
    client.close()
