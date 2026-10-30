import pytest
from agentmesh.core import Mesh,Agent,Task,Constraint
from agentmesh.observability import analyze_run

def test_agent_exception_preserves_trace_without_changing_type():
    def boom(value,task):
        raise RuntimeError("secret data must not enter diagnostics")
    mesh=Mesh(agents=[Agent("broken",boom)])
    with pytest.raises(RuntimeError) as failure:
        mesh.run(Task("diagnose"))
    trace=failure.value.agentmesh_trace
    assert trace[0]["agent"]=="broken"
    assert trace[0]["status"]=="error"
    assert trace[0]["error_type"]=="RuntimeError"
    assert "secret data" not in str(trace)
    diag=analyze_run({"accepted":False,"trace":trace})
    assert diag["suspected_causes"][0]["agent"]=="broken"

def test_bad_return_preserves_trace():
    mesh=Mesh(agents=[Agent("bad",lambda value,task:None)])
    with pytest.raises(TypeError) as failure:
        mesh.run(Task("diagnose"))
    assert failure.value.agentmesh_trace[0]["error_type"]=="TypeError"

def test_constraint_exception_is_visible():
    def broken_rule(_):raise ZeroDivisionError()
    mesh=Mesh(agents=[Agent("ok",lambda x,t:x)],max_attempts=1)
    result=mesh.run(Task("diagnose",[Constraint("broken-rule",broken_rule)]))
    assert not result.accepted
    assert any(e.get("agent")=="constraint:broken-rule" and e.get("error_type")=="ZeroDivisionError" for e in result.trace)

def test_failure_diagnostics_do_not_echo_output():
    diagnostic=analyze_run({"trace":[{"agent":"a","status":"error","error_type":"RuntimeError","output":"password=example"}]})
    assert "password=example" not in str(diagnostic)
