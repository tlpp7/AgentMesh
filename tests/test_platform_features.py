import pytest
from agentmesh.diagnostics import conditioning,residual_report
from agentmesh.integrations import AgentState,ToolSpec,ControlledAdapter,state_from_metrics
from agentmesh.storage import RunStore

def test_conditioning_identity():
    r=conditioning([[1,0],[0,1]])
    assert r["estimated_rank"]==2
    assert r["condition_number"]==pytest.approx(1)

def test_conditioning_singular():
    r=conditioning([[1,2],[2,4]])
    assert r["near_singular"] and r["condition_number"] is None

def test_residual_diagnostics():
    r=residual_report([[1,0],[0,1]],[2,3],[2,3])
    assert r["absolute_residual"]==0

def test_typed_agent_state():
    s=state_from_metrics(dict(latency_ms=20,error_rate=0,cost_units=1,quality_score=.9))
    assert s.vector()==[20,0,1,.9]
    with pytest.raises(ValueError): AgentState(0,2,0,.5)

def test_tools_denied_by_default():
    a=ControlledAdapter({"read":(ToolSpec("read"),lambda p:"secret")})
    assert a.invoke("read",{})["status"]=="denied"

def test_tools_need_allowlist():
    a=ControlledAdapter({"echo":(ToolSpec("echo",requires_approval=False),lambda x:x)})
    assert a.invoke("echo",{"hello":"world"})["result"]=={"hello":"world"}
    with pytest.raises(ValueError):a.invoke("missing",{})

def test_sqlite_runs(tmp_path):
    db=RunStore(tmp_path/"runs.sqlite3")
    rid=db.append("numeric",True,{"test":1})
    assert db.get(rid)=={"test":1}
    assert db.list()[0]["accepted"]
    assert db.get("unknown") is None

def test_sqlite_limit(tmp_path):
    db=RunStore(tmp_path/"runs.sqlite3")
    with pytest.raises(ValueError):db.list(1000)
