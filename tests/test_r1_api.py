"""R1 contract tests, only active when FastAPI/httpx optional packages are installed."""
import pytest
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from apps.api.main import create_app
from agentmesh.core import Mesh, Task
from agentmesh.constraints import nonempty, contains

@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("AGENTMESH_API_TOKEN",raising=False)
    return TestClient(create_app())

def test_health_contract(client):
    assert client.get("/api/health").json()=={
        "status":"ok","adapter":"fastapi","legacy_preserved":True}
    assert client.get("/").status_code==200

def test_legacy_engine_parity(client):
    payload={"objective":"Review pipeline","attempts":2,"contains":"impossible-placeholder"}
    response=client.post("/api/v2/run",json=payload)
    assert response.status_code==200
    expected=Mesh(max_attempts=2).run(Task(payload["objective"],[
        nonempty(),contains(payload["contains"])] )).to_dict()
    result=response.json()
    for key in ("accepted","output","attempts","violations"):
        assert result[key]==expected[key]
    assert "observability" in result

@pytest.mark.parametrize("body",[
    {"objective":" "},{"objective":"a","attempts":0},
    {"objective":"a","attempts":"3"},{"objective":"a","unknown":123}
])
def test_invalid_request_returns_422(client,body):
    assert client.post("/api/v2/run",json=body).status_code==422

def test_bearer_authorization(monkeypatch):
    monkeypatch.setenv("AGENTMESH_API_TOKEN","x"*40)
    client=TestClient(create_app())
    assert client.post("/api/v2/run",json={"objective":"hello"}).status_code==401
    assert client.post("/api/v2/run",json={"objective":"hello"},
        headers={"Authorization":"Bearer "+"x"*40}).status_code==200

def test_openapi_has_request_schema(client):
    document=client.get("/openapi.json").json()
    assert "/api/v2/run" in document["paths"]
    assert "RunRequest" in document["components"]["schemas"]
