from agentmesh.observability import analyze_run

def test_sequential_rejection_diagnostics():
    result=analyze_run({"accepted":False,"trace":[
        {"attempt":1,"agent":"analyzer","status":"ok","duration_ms":0.2},
        {"attempt":1,"supervisor":"rejected","violations":["contains:Review"]}]})
    assert result["event_count"]==2
    assert result["failure_count"]==1
    assert result["suspected_causes"][0]["category"]=="constraint_violation"
    assert "output" not in result["events"][0]

def test_adaptive_nested_trace():
    result=analyze_run({"mode":"hybrid","accepted":True,"output":{"trace":[
        {"attempt":1,"violations":["required:0"],"decision":"revise"},
        {"attempt":2,"violations":[],"decision":"accept"}]}})
    assert result["event_count"]==2
    assert result["agents"]["reviser"]==2

def test_numeric_budget_failure():
    result=analyze_run({"accepted":False,"feedback":{"converged":False,
        "iterations":50,"residual":.001}})
    assert result["failure_count"]==1
    assert result["suspected_causes"][0]["category"]=="iteration_budget_or_tolerance"

def test_limit_and_invalid_payload():
    import pytest
    with pytest.raises(TypeError): analyze_run([])
    with pytest.raises(ValueError): analyze_run({},max_events=0)
    result=analyze_run({"trace":[{"agent":"a","status":"ok"}]*10},max_events=3)
    assert result["truncated"] and result["event_count"]==3

def test_browser_contract():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    html=(root/"web/index.html").read_text()
    js=(root/"web/app.js").read_text()
    for key in ("traceSummary","traceTimeline","traceAgentFilter","loadPersistentTraces"):
        assert 'id="'+key+'"' in html
        assert key in js
