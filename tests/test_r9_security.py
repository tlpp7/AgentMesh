"""R9 isolated policy and FastAPI tests."""
import pytest
from agentmesh.security_policy import Principal,Policy,SlidingWindowLimiter

def test_role_is_explicit_and_unknown_roles_denied():
    policy=Policy()
    assert policy.allowed(Principal("viewer-1","viewer"),"runs:read")
    assert not policy.allowed(Principal("viewer-1","viewer"),"runs:execute")
    assert policy.allowed(Principal("operator-1","operator"),"runs:execute")
    with pytest.raises(ValueError):Principal("fake","admin")

def test_agent_capabilities_are_deny_by_default():
    policy=Policy()
    assert policy.agent_tool_allowed("analyzer","evaluate_trace")
    assert not policy.agent_tool_allowed("analyzer","review_issue")
    assert not policy.agent_tool_allowed("unknown","evaluate_trace")
    assert not policy.agent_tool_allowed("critic","github_write")

def test_rate_limit_and_window_recovery():
    clock=[0.]
    limiter=SlidingWindowLimiter(limit=2,window_seconds=10,clock=lambda:clock[0])
    assert limiter.accept("a") and limiter.accept("a")
    assert not limiter.accept("a")
    assert limiter.accept("b")
    clock[0]=11.
    assert limiter.accept("a")

def test_r9_api_enforcement(monkeypatch):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from apps.api.main import create_app
    monkeypatch.setenv("AGENTMESH_R9_ENFORCE","1")
    monkeypatch.setenv("AGENTMESH_R9_RATE_LIMIT","1")
    monkeypatch.setenv("AGENTMESH_API_TOKEN","a"*40)
    client=TestClient(create_app())
    body={"objective":"R9 controlled run"}
    assert client.post("/api/v2/run",json=body).status_code==401
    headers={"Authorization":"Bearer "+"a"*40}
    assert client.post("/api/v2/run",json=body,headers=headers).status_code==200
    assert client.post("/api/v2/run",json=body,headers=headers).status_code==429

def test_r9_requires_token_if_enforced(monkeypatch):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from apps.api.main import create_app
    monkeypatch.setenv("AGENTMESH_R9_ENFORCE","1")
    monkeypatch.delenv("AGENTMESH_API_TOKEN",raising=False)
    client=TestClient(create_app())
    assert client.post("/api/v2/run",json={"objective":"test"}).status_code==503
